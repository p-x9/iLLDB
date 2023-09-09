import UIKit

func windowHierarchy(_ window: UIWindow?, indentation: String = "", isLast: Bool = true, isSimple: Bool = false, isDetail: Bool = false) {
    guard let window = window else { return }

    var result = ""
    if isLast {
        result += "\(indentation)└─"
    } else {
        result += "\(indentation)├─"
    }

    let windowDescription: String
    if isDetail {
        windowDescription = "\(window)"
    } else if isSimple {
        windowDescription = "\(String(describing: type(of: window)))"
    } else {
        windowDescription = "\(String(describing: type(of: window))) \(window.frame)"
    }

    result += windowDescription
    print(result)

    if let rootViewController = window.rootViewController {
        viewControllerHierarchy(rootViewController, indentation: indentation + (isLast ? "   " : "│  "), isLast: true, isSimple: isSimple, isDetail: isDetail)
    }
}

func viewControllerHierarchy(_ viewController: UIViewController?, indentation: String = "", isLast: Bool = true, isSimple: Bool = false, isDetail: Bool = false) {
    guard let viewController = viewController else { return }

    var result = ""
    if isLast {
        result += "\(indentation)└─"
    } else {
        result += "\(indentation)├─"
    }

    let viewControllerDescription: String
    if isDetail {
        viewControllerDescription = "\(viewController)"
    } else if isSimple {
        viewControllerDescription = "\(String(describing: type(of: viewController)))"
    } else {
        viewControllerDescription = "\(String(describing: type(of: viewController))) \(viewController.view.frame))"
    }

    result += viewControllerDescription

    print(result)

    let children = viewController.children
    for (index, childViewController) in children.enumerated() {
        let isLastChild = index == children.count - 1
        viewControllerHierarchy(childViewController, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastChild, isSimple: isSimple, isDetail: isDetail)
    }

    for (index, subview) in viewController.view.subviews.enumerated() {
        let isLastSubview = index == viewController.view.subviews.count - 1
        viewHierarchy(subview, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastSubview, isSimple: isSimple, isDetail: isDetail)
    }
}

func viewHierarchy(_ view: UIView?, indentation: String = "", isLast: Bool = true, isSimple: Bool = false, isDetail: Bool = false) {
    guard let view = view else { return }

    var result = ""
    if isLast {
        result += "\(indentation)└─"
    } else {
        result += "\(indentation)├─"
    }

    let viewDescription: String
    if isDetail {
        viewDescription = "\(view)"
    } else if isSimple {
        viewDescription = "\(String(describing: type(of: view)))"
    } else {
        viewDescription = "\(String(describing: type(of: view))) \(view.frame)"
    }

    result += viewDescription

    print(result)

    for (index, subview) in view.subviews.enumerated() {
        let isLastSubview = index == view.subviews.count - 1
        viewHierarchy(subview, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastSubview, isSimple: isSimple, isDetail: isDetail)
    }
}
