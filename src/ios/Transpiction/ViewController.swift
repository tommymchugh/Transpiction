//
//  ViewController.swift
//  Transpiction
//
//  Created by Tommy McHugh on 10/30/19.
//  Copyright © 2019 Transpiction. All rights reserved.
//

import UIKit

class ViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        print("hello")
        
        let sampleLatentVector:[NSNumber] = [0, 1]
        let model = TofuModel()
        model?.generate(sampleLatentVector)
    }


}

