//
//  ViewController.swift
//  Transpiction
//
//  Created by Tommy McHugh on 10/30/19.
//  Copyright © 2019 Transpiction. All rights reserved.
//

import UIKit
import TensorFlowLite

extension Array {
    /// Creates a new array from the bytes of the given unsafe data.
    ///
    /// - Note: Returns `nil` if `unsafeData.count` is not a multiple of
    ///     `MemoryLayout<Element>.stride`.
    /// - Parameter unsafeData: The data containing the bytes to turn into an array.
    init?(unsafeData: Data) {
        guard unsafeData.count % MemoryLayout<Element>.stride == 0 else { return nil }
        let elements = unsafeData.withUnsafeBytes {
            UnsafeBufferPointer<Element>(
                start: $0,
                count: unsafeData.count / MemoryLayout<Element>.stride
            )
        }
        self.init(elements)
    }
}

extension Data {
    /// Creates a new buffer by copying the buffer pointer of the given array.
    ///
    /// - Warning: The given array's element type `T` must be trivial in that it can be copied bit
    ///     for bit with no indirection or reference-counting operations; otherwise, reinterpreting
    ///     data from the resulting buffer has undefined behavior.
    /// - Parameter array: An array with elements of type `T`.
    init<T>(copyingBufferOf array: [T]) {
        self = array.withUnsafeBufferPointer(Data.init)
    }
}

class ViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        print("hello")
        let modelName = "model"
        let modelExtension = "tflite"
        let modelPath = Bundle.main.path(forResource: modelName, ofType: modelExtension)
        
        do {
            
            let interpreter = try Interpreter(modelPath: modelPath!)
            
            var latentVector:[Float32] = []
            for index in 0..<100 {
                latentVector.append(Float32.random(in: 0...1))
            }
            let input = Data(copyingBufferOf: latentVector)
            try interpreter.resizeInput(at: 0, to: [100])
            try interpreter.allocateTensors()
            
            try interpreter.copy(input, toInputAt: 0)
            try interpreter.invoke()
            
            let output = try interpreter.output(at: 0)
            let results = [Float](unsafeData: output.data) ?? []
            print(results)
        } catch {
            print(error)
        }
    }


}

