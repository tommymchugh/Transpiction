//
//  TofuModel.m
//  Transpiction
//
//  Created by Tommy McHugh on 10/30/19.
//  Copyright © 2019 Transpiction. All rights reserved.
//
#import <LibTorch/LibTorch.h>
#import <stdio.h>
#import "TofuModel.h"

@implementation TofuModel {
    @protected
    torch::jit::script::Module _impl;
}

- (instancetype) init {
    self = [super init];
    if (self) {
        // Retrieve the file path for the model
        NSString* modelName = @"tofu";
        NSString* modelExtension = @"zip";
        NSString* filePath = [[NSBundle mainBundle] pathForResource:modelName ofType:modelExtension];
        
        // Setup the model
        try {
            _impl = torch::jit::load(filePath.UTF8String);
            _impl.eval();
        } catch (const std::exception& exception) {
            NSLog(@"%s", exception.what());
            return nil;
        }
    }
    return self;
}

- (nullable NSArray<NSNumber*>*) generate:(NSArray<NSNumber*>*)vector {
    // Convert latent vector to a tensor
    int lvSize = 100;
    at::Tensor latentVector = torch::tensor({ {1}});
    std::printf("%d", latentVector.dim());
    return nil;
}

@end
