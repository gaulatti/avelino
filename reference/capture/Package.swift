// swift-tools-version: 6.0
import PackageDescription
let package = Package(
    name: "AvelinoReferenceCapture",
    platforms: [.macOS(.v14)],
    dependencies: [.package(path: "../../.cache/reference-desktop")],
    targets: [.executableTarget(name: "AvelinoReferenceCapture", dependencies: [.product(name: "Sabella", package: "reference-desktop")])]
)
