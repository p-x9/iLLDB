import Foundation

func listFilesInDirectory(_ directoryURL: URL, indentation: String = "") {
    if indentation.isEmpty {
        let isDirectory = (try? directoryURL.resourceValues(forKeys: [.isDirectoryKey]))?.isDirectory == true
        print("\(isDirectory ? "📁 " : "📄 ")" + directoryURL.lastPathComponent)
    }

    do {
        let fileManager = FileManager.default
        let contents = try fileManager.contentsOfDirectory(at: directoryURL, includingPropertiesForKeys: nil, options: [])

        for (index, url) in contents.enumerated() {
            let isDirectory = (try? url.resourceValues(forKeys: [.isDirectoryKey]))?.isDirectory == true
            let isLast = index == contents.count - 1

            var fileHierarchy = "\(indentation)\(isLast ? "└─ " : "├─ ")"

            if isDirectory {
                fileHierarchy += "📁 \(url.lastPathComponent)"
                print(fileHierarchy)

                listFilesInDirectory(url, indentation: indentation + (isLast ? "   " : "│  "))
            } else {
                fileHierarchy += "📄 \(url.lastPathComponent)"
                print(fileHierarchy)
            }
        }
    } catch {
        print(error.localizedDescription)
    }
}
