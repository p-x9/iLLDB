// import UIKit
// typealias NSUIView = UIView
// typealias NSUIViewController = UIViewController
// typealias NSUIWindow = UIWindow
// typealias NSUIApplication = UIApplication

func windowHierarchy(_ window: NSUIWindow?, indentation: String = "", isLast: Bool = true, mode: String = "normal", depth: Int? = nil) {
    guard let window = window else { return }

    let currentDepth = indentation.replacingOccurrences(of: "│", with: " ").count / 3
    if let depth, currentDepth > depth {
        return
    }

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
    default:
        let frameDescription = frameDescription(window.frame)
        windowDescription = "\(String(describing: type(of: window))) \(frameDescription)"
    }

    result += windowDescription
    print(result)

    var rootViewController: NSUIViewController?
    if window.responds(to: Selector(("rootViewController"))) { // for iOS
        rootViewController = window.perform(Selector(("rootViewController"))).takeUnretainedValue() as? NSUIViewController
    } else if window.responds(to: Selector(("contentViewController"))) { // for macOS
        rootViewController = window.perform(Selector(("contentViewController"))).takeUnretainedValue() as? NSUIViewController
    }

    viewControllerHierarchy(rootViewController, indentation: indentation + (isLast ? "   " : "│  "), isLast: true, mode: mode, depth: depth)
}

func viewControllerHierarchy(_ viewController: NSUIViewController?, indentation: String = "", isLast: Bool = true, mode: String = "normal", depth: Int? = nil) {
    guard let viewController = viewController else { return }

    let currentDepth = indentation.replacingOccurrences(of: "│", with: " ").count / 3
    if let depth, currentDepth > depth {
        return
    }

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
    default:
        let frameDescription = frameDescription(viewController.view.frame)
        viewControllerDescription = "\(String(describing: type(of: viewController))) \(frameDescription))"
    }

    result += viewControllerDescription

    print(result)

    let children = viewController.children
    for (index, childViewController) in children.enumerated() {
        let isLastChild = index == children.count - 1 && viewController.view.subviews.isEmpty
        viewControllerHierarchy(childViewController, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastChild, mode: mode, depth: depth)
    }

    for (index, subview) in viewController.view.subviews.enumerated() {
        let isLastSubview = index == viewController.view.subviews.count - 1
        viewHierarchy(subview, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastSubview, mode: mode, depth: depth)
    }
}

func viewHierarchy(_ view: NSUIView?, indentation: String = "", isLast: Bool = true, mode: String = "normal", depth: Int? = nil) {
    guard let view = view else { return }

    let currentDepth = indentation.replacingOccurrences(of: "│", with: " ").count / 3
    if let depth, currentDepth > depth {
        return
    }

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
    default:
        let frameDescription = frameDescription(view.frame)
        viewDescription = "\(String(describing: type(of: view))) \(frameDescription)"
    }

    result += viewDescription

    print(result)

    for (index, subview) in view.subviews.enumerated() {
        let isLastSubview = index == view.subviews.count - 1
        viewHierarchy(subview, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastSubview, mode: mode, depth: depth)
    }
}

func layerHierarchy(_ layer: CALayer?, indentation: String = "", isLast: Bool = true, mode: String = "normal", depth: Int? = nil) {
    guard let layer = layer else { return }

    let currentDepth = indentation.replacingOccurrences(of: "│", with: " ").count / 3
    if let depth, currentDepth > depth {
        return
    }

    var result = ""
    if isLast {
        result += "\(indentation)└─"
    } else {
        result += "\(indentation)├─"
    }

    let layerDescription: String
    switch mode {
    case "simple": layerDescription = "\(String(describing: type(of: layer)))"
    case "detail": layerDescription = "\(layer)"
    default:
        let frameDescription = frameDescription(layer.frame)
        layerDescription = "\(String(describing: type(of: layer))) \(frameDescription)"
    }

    result += layerDescription

    print(result)

    guard let sublayers = layer.sublayers else { return }
    for (index, sublayer) in sublayers.enumerated() {
        let isLastSublayer = index == sublayers.count - 1
        layerHierarchy(sublayer, indentation: indentation + (isLast ? "   " : "│  "), isLast: isLastSublayer, mode: mode, depth: depth)
    }
}

func frameDescription(_ frame: CGRect) -> String {
    String(
        format: "(%.1f, %.1f, %.1f, %.1f)",
        arguments: [
            frame.x,
            frame.y,
            frame.width,
            frame.height
        ]
    )
}
