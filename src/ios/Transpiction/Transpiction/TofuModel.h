//
//  TofuModel.h
//  Transpiction
//
//  Created by Tommy McHugh on 10/30/19.
//  Copyright © 2019 Transpiction. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface TofuModel: NSObject
- (instancetype)init;
- (nullable NSArray<NSNumber*>*)generate:(NSArray<NSNumber*>*)vector;

@end
