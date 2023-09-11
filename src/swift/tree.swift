import UIKit

func windowHierarchy(_ window: UIWindow?, indentation: String = "", isLast: Bool = true, mode: String = "normal") {
    guard let window = window else { return }

    var result = ""
    if isLast {
        result += "\(indentation)└─"
    } else {
        result += "\(indentation)├─"
    }

    let windowDescription: String
    switch mode {
        case "simple": windowDescription = "\(String(describing: type(of: window)))"
        case "detail": windowDescription = "\(window)"
        default: windowDescription = "\(String(describing: type(of: window))) \(window.frame)"
    }

    result += windowDescription
    print(result)

    if let rootViewController = window.rootViewController {
        viewControllerHierarchy(rootViewController, indentation: indentation + (isLast ? "   " : "│  "), isLast: true, mode: mode)
    }
}

func viewControllerHierarchy(_ viewController: UIViewController?, indentation: String = "", isLast: Bool = true, mode: String = "normal") {
    guard let viewController = viewController else { return }

    var result = ""
    if isLast {
        result += "\(indentation)└─"
    } else {
        result += "\(indentation)├─"
    }

    let viewControllerDescription: String
    switch mode {
        case "simple": viewControllerDescription = "\(String(describing: type(of: viewController)))"
        case "detail": viewControllerDescription = "\(viewController)"
        default: viewControllerDescription = "\(String(describing: type(of: viewController))) \(viewController.view.frame))"
    }

    result += viewControllerDescription

    print(result)

    let children = viewController.children
    for (index, childViewController) in children.enumerated() {
        let isLastChild = index == children.count - 1
        viewControllerHierarchy(childViewController, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastChild, mode: mode)
    }

    for (index, subview) in viewController.view.subviews.enumerated() {
        let isLastSubview = index == viewController.view.subviews.count - 1
        viewHierarchy(subview, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastSubview, mode: mode)
    }
}

func viewHierarchy(_ view: UIView?, indentation: String = "", isLast: Bool = true, mode: String = "normal") {
    guard let view = view else { return }

    var result = ""
    if isLast {
        result += "\(indentation)└─"
    } else {
        result += "\(indentation)├─"
    }

    let viewDescription: String
    switch mode {
        case "simple": viewDescription = "\(String(describing: type(of: view)))"
        case "detail": viewDescription = "\(view)"
        default: viewDescription = "\(String(describing: type(of: view))) \(view.frame)"
    }

    result += viewDescription

    print(result)

    for (index, subview) in view.subviews.enumerated() {
        let isLastSubview = index == view.subviews.count - 1
        viewHierarchy(subview, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastSubview, mode: mode)
    }
}
