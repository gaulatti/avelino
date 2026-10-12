import AppKit
import CoreText
import SwiftUI
import Sabella

@MainActor
struct ButtonFixture: View {
    let variant: BleeckerButtonVariant
    let size: BleeckerButtonSize
    let disabled: Bool
    let dark: Bool
    var body: some View {
        BleeckerButton(variant: variant, size: size, action: {}) { Text("Publish") }
            .disabled(disabled)
            .frame(width: 240, height: 96)
            .background(dark ? BleeckerPalette.dark.background : BleeckerPalette.light.background)
            .environment(\.colorScheme, dark ? .dark : .light)
            .environment(\.bleeckerTextScale, 1)
    }
}

@MainActor
func run() throws {
    _ = NSApplication.shared
    let output = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "artifacts/reference"
    let directory = URL(fileURLWithPath: output, isDirectory: true)
    try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
    SabellaFonts.register()
    let variants: [(String, BleeckerButtonVariant)] = [("primary", .primary), ("secondary", .secondary), ("outline", .outline), ("subtle", .subtle), ("ghost", .ghost), ("link", .link), ("destructive", .destructive)]
    let sizes: [(String, BleeckerButtonSize)] = [("xs", .xs), ("sm", .sm), ("md", .md), ("lg", .lg)]
    var captures: [[String: Any]] = []
    for (appearance, dark) in [("light", false), ("dark", true)] {
        for (variantName, variant) in variants {
            for (sizeName, size) in sizes {
                for (state, disabled) in [("enabled", false), ("disabled", true)] {
                    let name = "button-\(appearance)-\(variantName)-\(sizeName)-\(state).png"
                    let renderer = ImageRenderer(content: ButtonFixture(variant: variant, size: size, disabled: disabled, dark: dark))
                    renderer.scale = 2
                    guard let cg = renderer.cgImage else { throw NSError(domain: "Capture", code: 1) }
                    let data = NSBitmapImageRep(cgImage: cg).representation(using: .png, properties: [:])!
                    try data.write(to: directory.appendingPathComponent(name))
                    captures.append(["path": name, "fixture": "button", "appearance": appearance, "variant": variantName,
                        "size": sizeName, "state": state, "width": 240, "height": 96, "dpr": 2, "textScale": 1,
                        "captureMethod": "SwiftUI.ImageRenderer (offscreen; does not capture native popup windows)",
                        "fonts": ["EncodeSans-Md"], "source": "fe8a1d462fbd793d883fb92086a16aa2947e32c9"])
                }
            }
        }
    }
    let manifest: [String: Any] = ["captures": captures, "os": ProcessInfo.processInfo.operatingSystemVersionString,
        "reference": "fe8a1d462fbd793d883fb92086a16aa2947e32c9", "graphicsBackend": "SwiftUI.ImageRenderer/CoreGraphics",
        "monospaceResolution": "No monospace in these fixtures; actual per-fixture resolution remains pending"]
    try JSONSerialization.data(withJSONObject: manifest, options: [.prettyPrinted, .sortedKeys]).write(to: directory.appendingPathComponent("captures.json"))
    print("Captured \(captures.count) pinned Sabella button cases; visual acceptance pending comparison")
}

try MainActor.assumeIsolated { try run() }
