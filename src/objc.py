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

        # inherites
        inherites_command = subparsers.add_parser("inherites",
                                                  help="Show class hierarchy of object",
                                                  formatter_class=util.HelpFormatter)
        inherites_command.add_argument("object",
                                       type=str,
                                       help="object")

        # methods
        method_command = subparsers.add_parser("methods",
                                               help="Show method list of object",
                                               formatter_class=util.HelpFormatter)
        method_command.add_argument("object",
                                    type=str,
                                    help="object")
        method_command.add_argument("--class", dest='class_name', type=str, help="Specify a target class in the inheritance hierarchy")
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

        if args.subcommand == "methods":
            self.methods(args, debugger, result)
        elif args.subcommand == "inherites":
            self.inherites(args, debugger, result)
        elif args.subcommand == "properties":
            self.properties(args, debugger, result)
        else:
            self.argparser.print_help()

    def inherites(
        self,
        args: argparse.Namespace,
        debugger: lldb.SBDebugger,
        result: lldb.SBCommandReturnObject
    ) -> None:
        inherites = self.class_inherites(debugger, args.object)
        result.AppendMessage(' -> '.join(inherites))

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

    def class_info(
        self,
        debugger: lldb.SBDebugger,
        object: str,
        class_name: Optional[str]
    ) -> Optional['ClassInfo']:
        inherites = self.class_inherites(debugger, object)
        if class_name is not None and class_name not in inherites:
            return None
        if class_name is None:
            class_name = inherites[-1]

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

    def class_inherites(
        self,
        debugger: lldb.SBDebugger,
        object: str,
    ) -> list[str]:
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


from dataclasses import dataclass


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
    class_methods: list[Method]
    instance_methods: list[Method]
    properties: list[Property]

    def __str__(self) -> str:
        class_methods_description = "\n".join(list(map(lambda m: f"    {m}", self.class_methods)))
        instance_methods_description = "\n".join(list(map(lambda m: f"    {m}", self.instance_methods)))
        properties_description = "\n".join(list(map(lambda p: f"    {p}", self.properties)))

        description = f"Class Methods:\n{class_methods_description}" + "\n \n"
        description += f"Instance Methods:\n{instance_methods_description}" + "\n \n"
        description += f"Properties:\n{properties_description}"

        return description


class ClassInfoParser:
    @classmethod
    def parse(cls, string: str) -> ClassInfo:
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
    def parse_methods(cls, lines: list[str], is_static: bool = False) -> list[Method]:
        operator = '+' if is_static else '-'
        lines = list(filter(lambda l: l[0:5] == f'		{operator} (', lines))
        lines = list(map(lambda l: l[2:], lines))
        methods = list[Method]()

        for line in lines:
            lines = line.replace('	', '')
            components = line.split('; ')
            name = components[0] + ';'
            ptr = components[1].replace('(', '').replace(')', '')

            methods.append(Method(name, ptr))

        return methods

    @classmethod
    def parse_properties(cls, lines: list[str]) -> list[Property]:
        lines = list(filter(lambda l: '@property' in l, lines))
        lines = list(map(lambda l: l[2:], lines))
        properties = list[Property]()

        for line in lines:
            lines = line.replace('	', '')
            components = line.split('; ')
            name = components[0] + ';'
            name = name.replace(';;', ';')

            dynamic: Optional[str] = None
            if len(components) > 1:
                dynamic = components[1].replace('( ', '').replace(' )', '')

            properties.append(Property(name, dynamic))

        return properties
