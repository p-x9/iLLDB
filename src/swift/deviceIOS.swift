import UIKit

var screenSize: CGSize {
    guard let window = UIApplication.shared.connectedScenes.first as? UIWindowScene else {
        return .zero
    }
    return window.screen.bounds.size
}

func printDeviceInfo() {
    let currentDevice = UIDevice.current

    print("[Device Info]")
    print("Name:              \(currentDevice.name)")
    print("Model:             \(currentDevice.model)")
    print("IsSimulator:       \(TARGET_OS_SIMULATOR != 0)")
    print("System Name:       \(currentDevice.systemName)")
    print("System Version:    \(currentDevice.systemVersion)")
    print("Screen:            \(screenSize.width) x \(screenSize.height)")
    print("Locale:            \(Locale.current)")
    if let identifierForVendor = currentDevice.identifierForVendor {
        print("Id For Vendor:     \(identifierForVendor.uuidString)")
    }
}
