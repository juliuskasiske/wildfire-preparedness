import Foundation
import Vision
import CoreImage
let args=CommandLine.arguments
guard args.count>=2, let img=CIImage(contentsOf: URL(fileURLWithPath:args[1])) else { exit(1) }
let h=VNImageRequestHandler(ciImage:img, options:[:])
let r=VNDetectBarcodesRequest()
try h.perform([r])
guard let res=r.results, !res.isEmpty else { print("NO BARCODE FOUND"); exit(2) }
for b in res {
    print("symbology: \(b.symbology.rawValue)")
    print("payload  : \(b.payloadStringValue ?? "(none)")")
}
