//
//  contact+extension.swift
//  RWCards
//
//  Created by Alex Cruz on 9/6/18.
//  Copyright © 2018 Raywenderlich. All rights reserved.
//

import UIKit

extension Contact {
    func contactTypeToString() -> String {
        switch type {
        case .speaker:
            return "SPEAKER"
        case .attendant:
            return "ATTENDEE"
        case .volunteer:
            return "VOLUNTEER"
        default:
            return "UNKNOWN"
        }
    }
}
