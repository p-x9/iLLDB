import Foundation

func listFilesInDirectory(_ directoryURL: URL, level: Int = 0) {
    if level == 0 {
        let isDirectory = (try? directoryURL.resourceValues(forKeys: [.isDirectoryKey]))?.isDirectory == true
        print("\(isDirectory ? "📁 " : "📄 ")" + directoryURL.lastPathComponent)
    }

    var fileHierarchy = ""

    do {
        let fileManager = FileManager.default
        let contents = try fileManager.contentsOfDirectory(at: directoryURL, includingPropertiesForKeys: nil, options: [])

        for (index, url) in contents.enumerated() {
            let isDirectory = (try? url.resourceValues(forKeys: [.isDirectoryKey]))?.isDirectory == true
            let indentation = String(repeating: "│  ", count: level) + (index == contents.count - 1 ? "└─ " : "├─ ")

            if isDirectory {
                fileHierarchy = "\(indentation)📁 \(url.lastPathComponent)"
                print(fileHierarchy)
                listFilesInDirectory(url, level: level + 1)
            } else {
                fileHierarchy = "\(indentation)📄 \(url.lastPathComponent)"
                print(fileHierarchy)
            }
        }
    } catch {
        print(error.localizedDescription)
    }
}
