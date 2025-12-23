#include "driver/adc.h"
#include "driver/adc_types_legacy.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <stdio.h>

#define ADC_CHANNEL ADC1_CHANNEL_6

void app_main(void) {
  adc1_config_width(ADC_WIDTH_BIT_12);

  while (1) {
    int raw_value = adc1_get_raw(ADC_CHANNEL);
    printf("%d\n", raw_value);
  }
}
