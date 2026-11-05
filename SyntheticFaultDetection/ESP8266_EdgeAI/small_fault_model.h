// Otomatik üretilmiş Edge AI Model Dosyası
#ifndef SMALL_FAULT_MODEL_H
#define SMALL_FAULT_MODEL_H

#include <Arduino.h>

String predictFault(float features[]) {
    if (features[4] <= 0.2920) {
        if (features[5] <= 1.5354) {
            return "Dengesizlik";
        } else {
            return "Yatay_Hizasizlik";
        }
    } else {
        if (features[13] <= 0.3726) {
            return "Normal";
        } else {
            return "Dikey_Hizasizlik";
        }
    }

}

#endif
