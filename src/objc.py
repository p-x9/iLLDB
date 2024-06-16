import lldb
import shlex
import argparse
from typing import Union, Optional, cast
from lldbhelper import LLDBCommandBase
import util


def __lldb_init_module(debugger: lldb.SBDebugger, internal_dict: dict) -> None:
    ObjcCommnad.register_lldb_command(debugger, ObjcCommnad.__module__)


class ObjcCommnad(LLDBCommandBase):

    @classmethod
    def cmdname(cls) -> str:
        return 'objc'

    @classmethod
    def description(cls) -> str:
        return 'Objective-C runtime debugging. [iLLDB]'

    def create_argparser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Objective-C runtime debugging",
            formatter_class=util.HelpFormatter
        )
        subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

        # inherits
        inherits_command = subparsers.add_parser("inherits",
                                                 help="Show class hierarchy of object",
                                                 formatter_class=util.HelpFormatter)
        inherits_command.add_argument("object",
                                      type=str,
                                      help="object")

        # methods
        method_command = subparsers.add_parser("methods",
                                               help="Show method list of object",
                                               formatter_class=util.HelpFormatter)
        method_command.add_argument("object",
                                    type=str,
                                    help="object")
        method_command.add_argument("--class",
                                    dest='class_name',
                                    type=str,
                                    help="Specify a target class in the inheritance hierarchy")
        method_command.add_argument("-c", "--class-only", action="store_true", help="Show only class methods")
        method_command.add_argument("-i", "--instance-only", action="store_true", help="Show only instance methods")

        # properties
        properties_command = subparsers.add_parser("properties",
                                                   help="Show property list of object",
                                                   formatter_class=util.HelpFormatter)
        properties_command.add_argument("object",
                                        type=str,
                                        help="object")
        properties_command.add_argument("--class",
                                        dest='class_name',
                                        type=str,
                                        help="Specify a target class in the inheritance hierarchy")

        # ivars
        ivars_command = subparsers.add_parser("ivars",
                                              help="Show ivar list of object",
                                              formatter_class=util.HelpFormatter)
        ivars_command.add_argument("object",
                                   type=str,
                                   help="object")
        ivars_command.add_argument("--class",
                                   dest='class_name',
                                   type=str,
                                   help="Specify a target class in the inheritance hierarchy")

        return parser

    def __call__(
        self,
        debugger: lldb.SBDebugger,
        command: str,
        exe_ctx: lldb.SBExecutionContext,
        result: lldb.SBCommandReturnObject
    ) -> None:
        args: Union[list[str], argparse.Namespace] = shlex.split(command, posix=False)
        args = self.argparser.parse_args(cast(list[str], args))
        args = cast(argparse.Namespace, args)

        if args.subcommand == "methods":
            self.methods(args, debugger, result)
        elif args.subcommand == "inherits":
            self.inherits(args, debugger, result)
        elif args.subcommand == "properties":
            self.properties(args, debugger, result)
        elif args.subcommand == "ivars":
            self.ivars(args, debugger, result)
        else:
            self.argparser.print_help()

    def inherits(
        self,
        args: argparse.Namespace,
        debugger: lldb.SBDebugger,
        result: lldb.SBCommandReturnObject
    ) -> None:
        inherits = self.class_inherits(debugger, args.object)
        result.AppendMessage(' -> '.join(inherits))

    def methods(
        self,
        args: argparse.Namespace,
        debugger: lldb.SBDebugger,
        result: lldb.SBCommandReturnObject
    ) -> None:
        class_info = self.class_info(
            debugger,
            args.object,
            args.class_name
        )

        if class_info is None:
            if args.class_name is not None:
                result.AppendMessage("Invalid class name")
            else:
                result.AppendMessage('Invalid object')
            return

        show_all = (not args.class_only and not args.instance_only)
        text = ""
        if args.class_only or show_all:
            text += "Class Methods\n"
            text += '\n'.join(map(lambda m: f"    {m.name}", class_info.class_methods))
            text += '\n'

        if args.instance_only or show_all:
            text += "Instance Methods\n"
            text += '\n'.join(map(lambda m: f"    {m.name}", class_info.instance_methods))
            text += '\n'

        result.AppendMessage(text)

    def properties(
        self,
        args: argparse.Namespace,
        debugger: lldb.SBDebugger,
        result: lldb.SBCommandReturnObject
    ) -> None:
        class_info = self.class_info(
            debugger,
            args.object,
            args.class_name
        )

        if class_info is None:
            if args.class_name is not None:
                result.AppendMessage("Invalid class name")
            else:
                result.AppendMessage('Invalid object')
            return

        text = "Properties\n"
        text += '\n'.join(map(lambda p: f"    {p.name}", class_info.properties))
        text += '\n'

        result.AppendMessage(text)

    def ivars(
        self,
        args: argparse.Namespace,
        debugger: lldb.SBDebugger,
        result: lldb.SBCommandReturnObject
    ) -> None:
        ivars = self.class_ivars(
            debugger,
            args.object,
            args.class_name
        )

        text = "Ivars:\n"
        text += '\n'.join(map(lambda v: f"    {v}", ivars))
        result.AppendMessage(text)

    def class_info(
        self,
        debugger: lldb.SBDebugger,
        object: str,
        class_name: Optional[str]
    ) -> Optional['ClassInfo']:
        """
        Retrieves information about a specific class in the Objective-C runtime.

        Args:
            debugger (lldb.SBDebugger):
                An instance of the LLDB debugger.
            object (str):
                The name of the object for which to retrieve class information.
            class_name (Optional[str]):
                The name of the class for which to retrieve information.
                If not provided, the last class in the object's class hierarchy will be used.

        Returns:
            Optional['ClassInfo']:
                The parsed class information, including class methods, instance methods, and properties.
                Returns None if the class name is invalid or the object is invalid.
        """
        inherits = self.class_inherits(debugger, object)
        if class_name is not None and class_name not in inherits:
            return None
        if class_name is None:
            class_name = inherits[-1]

        script: str

        language: int = lldb.eLanguageTypeObjC
        if util.currentLanguage(debugger) == lldb.eLanguageTypeSwift:
            script = f"""
            {object}.perform(Selector(("__methodDescriptionForClass:")), with: NSClassFromString("{class_name}"))
            """
            language = lldb.eLanguageTypeSwift
        else:
            script = f"""
            (NSString *)[{object} __methodDescriptionForClass: NSClassFromString(@"{class_name}")];
            """

        ret = util.exp_script(
            debugger,
            script,
            lang=language
        )

        return ClassInfoParser.parse(ret.GetObjectDescription())

    def class_inherits(
        self,
        debugger: lldb.SBDebugger,
        object: str,
    ) -> list[str]:
        """
        Retrieve the class hierarchy of an object in Objective-C or Swift.

        Args:
            debugger (lldb.SBDebugger): An instance of `lldb.SBDebugger` used for debugging.
            object (str): The name of the object for which to retrieve the class hierarchy.

        Returns:
            list[str]: A list of class names representing the class hierarchy of the object.
        """

        script: str

        language: int = lldb.eLanguageTypeObjC_plus_plus
        if util.currentLanguage(debugger) == lldb.eLanguageTypeSwift:
            script = f"""
            var currentClass: AnyClass? = object_getClass({object})
            var result = String(describing: type(of: {object}))

            while true {{
                if let current = currentClass,
                   let superClass = class_getSuperclass(current) {{
                    result = "\\(String(describing: superClass)), " + result
                    currentClass = superClass
                }} else {{
                    break
                }}
            }}

            result
            """
            language = lldb.eLanguageTypeSwift
        else:
            script = f"""
            Class currentClass = (Class)object_getClass({object});
            NSMutableString *result = [NSMutableString stringWithFormat:@"%s", (char *)class_getName(currentClass)];

            while ((currentClass = (Class)class_getSuperclass(currentClass))) {{
                [result insertString:[NSString stringWithFormat:@"%s, ", (char *)class_getName(currentClass)] atIndex:0];
            }}
            result;
            """

        ret = util.exp_script(
            debugger,
            script,
            lang=language
        )

        if ret:
            result: str = ret.asStr()
            return result.split(', ')
        else:
            return []

    def class_ivars(
        self,
        debugger: lldb.SBDebugger,
        object: str,
        class_name: Optional[str]
    ) -> list['IVar']:
        inherits = self.class_inherits(debugger, object)
        if class_name is not None and class_name not in inherits:
            return []
        if class_name is None:
            class_name = inherits[-1]

        script = ''

        language: int = lldb.eLanguageTypeObjC
        if util.currentLanguage(debugger) == lldb.eLanguageTypeSwift:
            script = f"""
            {object}.perform(Selector(("__ivarDescriptionForClass:")), with: NSClassFromString("{class_name}"))
            """
            language = lldb.eLanguageTypeSwift
        else:
            script = f"""
            (NSString *)[{object} __ivarDescriptionForClass: NSClassFromString(@"{class_name}")];
            """

        ret = util.exp_script(
            debugger,
            script,
            lang=language
        )

        return IVarParser.parse(ret.GetObjectDescription())


from dataclasses import dataclass
import re


@dataclass
class Method:
    name: str
    ptr: str

    def isClassMethod(self) -> bool:
        return self.name[0] == '+'

    def __str__(self) -> str:
        return f"{self.name} ({self.ptr})"


@dataclass
class Property:
    name: str
    dynamic: Optional[str]

    def __str__(self) -> str:
        if self.dynamic:
            return f"{self.name} ({self.dynamic})"
        return f"{self.name}"


@dataclass
class ClassInfo:
    """
    A data class that represents information about a class in Objective-C.

    Attributes:
        class_methods (list[Method]):
            A list of Method objects representing the class methods of the class.
        instance_methods (list[Method]):
            A list of Method objects representing the instance methods of the class.
        properties (list[Property]):
            A list of Property objects representing the properties of the class.
    """

    class_methods: list[Method]
    instance_methods: list[Method]
    properties: list[Property]

    def __str__(self) -> str:
        """
        Returns a string representation of the class information.

        Returns:
            str: A string representation of the class information.
        """
        class_methods_description = "\n".join(list(map(lambda m: f"    {m}", self.class_methods)))
        instance_methods_description = "\n".join(list(map(lambda m: f"    {m}", self.instance_methods)))
        properties_description = "\n".join(list(map(lambda p: f"    {p}", self.properties)))

        description = f"Class Methods:\n{class_methods_description}" + "\n \n"
        description += f"Instance Methods:\n{instance_methods_description}" + "\n \n"
        description += f"Properties:\n{properties_description}"

        return description


class ClassInfoParser:
    """
    This class is responsible for parsing a string representation of class information and converting it into a `ClassInfo` object.

    Example Usage:
    ```python
    string = "		+ (void)classMethod1;\n		- (void)instanceMethod1;\n		@property (nonatomic, strong) NSString *property1;\n"
    class_info = ClassInfoParser.parse(string)
    print(class_info)
    ```
    Expected Output:
    ```
    Class Methods:
        + (void)classMethod1
    Instance Methods:
        - (void)instanceMethod1
    Properties:
        property1
    ```

    Methods:
    - parse(string: str) -> ClassInfo:
        Parses the given string representation of class information and returns a `ClassInfo` object.
    - parse_methods(lines: List[str], is_static: bool = False) -> List[Method]:
        Parses the given list of lines and extracts the class methods or instance methods based on the value of the `is_static` parameter.
    - parse_properties(lines: List[str]) -> List[Property]:
        Parses the given list of lines and extracts the properties.
    """

    @classmethod
    def parse(cls, string: str) -> ClassInfo:
        """
        Parses the given string representation of class information and returns a `ClassInfo` object.

        Args:
            string (str): The string representation of class information.

        Returns:
            ClassInfo: The parsed `ClassInfo` object.
        """
        lines = string.splitlines()
        class_methods = cls.parse_methods(lines, is_static=True)
        instance_methods = cls.parse_methods(lines, is_static=False)
        properties = cls.parse_properties(lines)

        return ClassInfo(
            class_methods=class_methods,
            instance_methods=instance_methods,
            properties=properties
        )

    @classmethod
    def parse_methods(
        cls,
        lines: list[str],
        is_static: bool = False
    ) -> list[Method]:
        """
        Parses the given list of lines and extracts the class methods or instance methods based on the value of the `is_static` parameter.

        Args:
            lines (list[str]): The list of lines to parse.
            is_static (bool, optional): Indicates whether to parse class methods (True) or instance methods (False). Defaults to False.

        Returns:
            list[Method]: The list of parsed methods.
        """
        operator = '+' if is_static else '-'
        lines = list(filter(lambda l: l[0:5] == f'		{operator} (', lines))
        lines = list(map(lambda l: l[2:], lines))
        methods = list[Method]()

        for line in lines:
            line = line.replace('	', '')
            components = line.split('; ')
            name = components[0] + ';'
            ptr = components[1].replace('(', '').replace(')', '')

            methods.append(Method(name, ptr))

        return methods

    @classmethod
    def parse_properties(cls, lines: list[str]) -> list[Property]:
        """
        Parses the given list of lines and extracts the properties.

        Args:
            lines (list[str]): The list of lines to parse.

        Returns:
            list[Property]: The list of parsed properties.
        """
        lines = list(filter(lambda l: '@property' in l, lines))
        lines = list(map(lambda l: l[2:], lines))
        properties = list[Property]()

        for line in lines:
            line = line.replace('	', '')
            components = line.split('; ')
            name = components[0] + ';'
            name = name.replace(';;', ';')

            dynamic: Optional[str] = None
            if len(components) > 1:
                dynamic = components[1].replace('( ', '').replace(' )', '')

            properties.append(Property(name, dynamic))

        return properties


@dataclass
class IVar:
    """
    Represents an instance variable in Objective-C.

    Attributes:
        name (str): The name of the instance variable.
        type (str): The type of the instance variable.
        value (str): The value of the instance variable.
    """

    name: str
    type: str
    value: str

    def __str__(self) -> str:
        """
        Returns a string representation of the instance variable.

        Returns:
            str: The string representation of the instance variable.
        """
        return f"{self.name} = ({self.type}) {self.value}"


class IVarParser:
    """
    A class for parsing a string representation of Objective-C instance variables and converting them into a list of IVar objects.
    """

    @classmethod
    def parse(cls, string: str) -> list:
        """
        Parses a string representation of Objective-C instance variables and returns a list of IVar objects.

        Args:
            string (str): The string representation of Objective-C instance variables.

        Returns:
            list: A list of IVar objects.

        Example:
            string = "	_debugName (NSString*): @"UIWindow-0x10950ea70-0""
            ivars = IVarParser.parse(string)
            for ivar in ivars:
                print(ivar.name)
                print(ivar.type)
                print(ivar.value)

            Output:
            _debugName
            NSString *
            @"UIWindow-0x10950ea70-0""
        """
        lines = string.splitlines()

        ivars = list[IVar]()

        for i, line in enumerate(lines):
            if line.startswith('		'):
                ivars[-1].value += f"\n{line}"
            elif line.startswith('	}'):
                ivars[-1].value += "\n	}"
            elif line.startswith('	'):
                components = line.split(' ')
                name = components[0].replace('	', '')

                type_match = re.search(r'\((.*?)\)', line)
                if type_match is not None:
                    type = type_match.group(1)
                    value = line[type_match.end() + 2:]
                    ivars.append(IVar(name, type, value))

        return ivars
