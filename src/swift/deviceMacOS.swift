import Foundation
import SystemConfiguration

func printDeviceInfo() {
    let processInfo = ProcessInfo.processInfo

    print("[Device Info]")
    if let name = SCDynamicStoreCopyComputerName(nil, nil) {
        print("Name:           \(name)")
    }

    if let model = sysctlByString(key: "hw.model") {
        print("Model:          \(model)")
    }

    print("System Name:    macOS")
    print("System Version: \(processInfo.operatingSystemVersionString)")

    if let cpu = sysctlByString(key: "machdep.cpu.brand_string") {
        print("CPU:            \(cpu)")
    }

    print("Locale:         \(Locale.current)")
}

func sysctlByString(key: String) -> String? {
    var size: size_t = 0
    sysctlbyname(key, nil, &size, nil, 0)
    var value = [CChar](repeating: 0,  count: Int(size))
    sysctlbyname(key, &value, &size, nil, 0)

    return String(cString: value)
}
