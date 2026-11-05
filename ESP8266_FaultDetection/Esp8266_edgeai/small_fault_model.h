#ifndef SMALL_FAULT_MODEL_H
#define SMALL_FAULT_MODEL_H

// Otomatik oluşturulmuş Edge AI Karar Ağacı Header Dosyası
inline int predictFault(float features[]) {
    if (features[3] <= 1.295000) {
        return 0;
    } else {
        if (features[14] <= 9.597190) {
            if (features[13] <= 1.261681) {
                if (features[15] <= 4.000000) {
                    if (features[6] <= 0.483000) {
                        return 3;
                    } else {
                        return 2;
                    }
                } else {
                    if (features[11] <= 8.690000) {
                        return 1;
                    } else {
                        return 2;
                    }
                }
            } else {
                if (features[8] <= 1.482004) {
                    return 3;
                } else {
                    if (features[11] <= 11.355000) {
                        return 1;
                    } else {
                        return 2;
                    }
                }
            }
        } else {
            if (features[10] <= -3.650000) {
                return 1;
            } else {
                if (features[1] <= 2.065949) {
                    return 3;
                } else {
                    return 1;
                }
            }
        }
    }
}

#endif