import Foundation
import Vision
import CoreImage
import AppKit

let args = CommandLine.arguments
guard args.count >= 3, let img = CIImage(contentsOf: URL(fileURLWithPath: args[1])) else {
    FileHandle.standardError.write("usage: cutout <in> <out>\n".data(using:.utf8)!); exit(1)
}
let handler = VNImageRequestHandler(ciImage: img, options: [:])
let req = VNGenerateForegroundInstanceMaskRequest()
do {
    try handler.perform([req])
    guard let obs = req.results?.first else {
        FileHandle.standardError.write("no foreground instance found\n".data(using:.utf8)!); exit(2)
    }
    print("instances found: \(obs.allInstances.count)")
    let buf = try obs.generateMaskedImage(ofInstances: obs.allInstances,
                                          from: handler,
                                          croppedToInstancesExtent: true)
    let ci = CIImage(cvPixelBuffer: buf)
    print("cutout extent: \(Int(ci.extent.width)) x \(Int(ci.extent.height))")
    let ctx = CIContext()
    try ctx.writePNGRepresentation(of: ci, to: URL(fileURLWithPath: args[2]),
                                   format: .RGBA8,
                                   colorSpace: CGColorSpaceCreateDeviceRGB())
    print("wrote \(args[2])")
} catch {
    FileHandle.standardError.write("error: \(error)\n".data(using:.utf8)!); exit(3)
}
