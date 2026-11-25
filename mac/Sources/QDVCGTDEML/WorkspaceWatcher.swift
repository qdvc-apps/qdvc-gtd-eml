import CoreServices
import Foundation
import GTDCore

/// Watches a workspace on disk with FSEvents, so changes made by the CLI,
/// Finder or a sync tool appear without waiting for the app to be activated
/// (the GTK 4 edition's file monitors). Only the workspace's own files count:
/// `metadata.csv`, `workspace.yml`, the six workflow folders and the `.eml`
/// files in them. Hidden and temporary files (such as the ones atomic writes
/// make) are ignored.
///
/// The owner must call `stop()` before letting go of the watcher: the
/// stream refers to it without retaining it.
@MainActor
final class WorkspaceWatcher {
    private let root: URL
    private let onChange: @MainActor ([String]) -> Void
    private var stream: FSEventStreamRef?

    init(root: URL, onChange: @escaping @MainActor ([String]) -> Void) {
        self.root = root
        self.onChange = onChange
    }

    /// Start watching; false if FSEvents could not watch the folder.
    @discardableResult
    func start() -> Bool {
        guard stream == nil else { return true }
        var context = FSEventStreamContext(version: 0,
                                           info: Unmanaged.passUnretained(self).toOpaque(),
                                           retain: nil, release: nil, copyDescription: nil)
        let flags = FSEventStreamCreateFlags(kFSEventStreamCreateFlagUseCFTypes
                                             | kFSEventStreamCreateFlagFileEvents
                                             | kFSEventStreamCreateFlagWatchRoot)
        guard let created = FSEventStreamCreate(kCFAllocatorDefault, workspaceWatcherCallback, &context,
                                                [root.path] as CFArray,
                                                FSEventStreamEventId(kFSEventStreamEventIdSinceNow),
                                                0.3, flags) else { return false }
        FSEventStreamSetDispatchQueue(created, DispatchQueue.main)
        guard FSEventStreamStart(created) else {
            FSEventStreamInvalidate(created)
            FSEventStreamRelease(created)
            return false
        }
        stream = created
        return true
    }

    func stop() {
        guard let current = stream else { return }
        FSEventStreamStop(current)
        FSEventStreamInvalidate(current)
        FSEventStreamRelease(current)
        stream = nil
    }

    fileprivate func deliver(_ paths: [String]) {
        let relevant = paths.filter { WorkspaceWatcher.isRelevant($0, root: root) }
        if !relevant.isEmpty { onChange(relevant) }
    }

    /// True for a path that is one of the workspace's own files or folders.
    /// FSEvents reports real paths, so the root's symbolic links (such as
    /// /var → /private/var) are resolved before comparing.
    nonisolated static func isRelevant(_ path: String, root: URL) -> Bool {
        let base = root.resolvingSymlinksInPath().standardizedFileURL.path
        let url = URL(fileURLWithPath: path).standardizedFileURL
        let name = url.lastPathComponent
        if name.hasPrefix(".") || name.hasSuffix(".tmp") { return false }
        let parent = url.deletingLastPathComponent().path
        let folderNames = Set(Folder.allCases.map(\.rawValue))
        if url.path == base { return true }
        if parent == base {
            return name == "metadata.csv" || name == WorkspaceConfig.fileName || folderNames.contains(name)
        }
        let grandparent = url.deletingLastPathComponent().deletingLastPathComponent().path
        return grandparent == base && folderNames.contains((parent as NSString).lastPathComponent)
            && name.lowercased().hasSuffix(".eml")
    }
}

/// The FSEvents callback. A file-scope function, so it is a plain C function
/// pointer with no actor isolation; the stream delivers on the main queue,
/// where the watcher lives.
private func workspaceWatcherCallback(_ streamRef: ConstFSEventStreamRef,
                                      _ info: UnsafeMutableRawPointer?,
                                      _ count: Int,
                                      _ eventPaths: UnsafeMutableRawPointer,
                                      _ eventFlags: UnsafePointer<FSEventStreamEventFlags>,
                                      _ eventIDs: UnsafePointer<FSEventStreamEventId>) {
    guard let info else { return }
    let array = Unmanaged<CFArray>.fromOpaque(eventPaths).takeUnretainedValue() as NSArray
    let paths = array.compactMap { $0 as? String }
    let watcher = Unmanaged<WorkspaceWatcher>.fromOpaque(info).takeUnretainedValue()
    MainActor.assumeIsolated { watcher.deliver(paths) }
}
