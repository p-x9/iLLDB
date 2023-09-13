import UIKit

func printDeviceInfo() {
    let currentDevice = UIDevice.current

    print("[Device Info]")
    print("Name:              \(currentDevice.name)")
    print("Model:             \(currentDevice.model)")
    print("System Name:       \(currentDevice.systemName)")
    print("System Version:    \(currentDevice.systemVersion)")
    if let identifierForVendor = currentDevice.identifierForVendor {
        print("Id For Vendor:     \(identifierForVendor.uuidString)")
    }
}
