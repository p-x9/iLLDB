import Foundation

func printAppInfo() {
    guard let appInfo = Bundle.main.infoDictionary else {
        return
    }
    print("[App Info]")
    if let appName = appInfo["CFBundleName"] as? String {
        print("App Name:          \(appName)")
    }
    if let appVersion = appInfo["CFBundleShortVersionString"] as? String {
        print("App Version:       \(appVersion)")
    }
    if let appBuild = appInfo["CFBundleVersion"] as? String {
        print("App Build Number:  \(appBuild)")
    }
    if let bundleIdentifier = appInfo["CFBundleIdentifier"] as? String {
        print("Bundle Identifier: \(bundleIdentifier)")
    }
    if let executableName = appInfo["CFBundleExecutable"] as? String {
        print("Executable Name:   \(executableName)")
    }
    if let bundleDisplayName = appInfo["CFBundleDisplayName"] as? String {
        print("Display Name:      \(bundleDisplayName)")
    }
    if let bundleIconFile = appInfo["CFBundleIconFile"] as? String {
        print("Icon File:         \(bundleIconFile)")
    }
    if let bundleIconFiles = appInfo["CFBundleIconFiles"] as? [String] {
        print("Icon Files:        \(bundleIconFiles)")
    }
}
