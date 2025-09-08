<template>
  <v-card elevation="1" class="chart-card">
    <v-card-text>
      <div class="d-flex justify-space-between align-center mb-6">
        <div>
          <h3 class="text-h5 font-weight-bold">{{ t('charts.platformDistribution.title') }}</h3>
          <p class="text-body-2 text-medium-emphasis">{{ t('charts.platformDistribution.subtitle') }}</p>
        </div>
      </div>

      <div class="chart-container">
        <apexchart 
          type="donut" 
          height="300" 
          :options="chartOptions" 
          :series="chartSeries" 
          ref="chart"
        />
      </div>

      <div class="d-flex justify-center mt-4">
        <div class="d-flex align-center gap-6">
          <div v-for="(item, index) in platformData" :key="index" class="d-flex align-center gap-2">
            <div 
              class="platform-indicator" 
              :style="{ backgroundColor: item.color }"
            ></div>
            <span class="text-body-2">{{ item.name }}</span>
            <span class="text-body-2 font-weight-bold">{{ item.value }}</span>
          </div>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { useModuleI18n } from '@/i18n/composables';

export default {
  name: 'PlatformStat',
  props: ['stat'],
  setup() {
    const { tm: t } = useModuleI18n('features/dashboard');
    
    // Reactive data
    const platformData = ref([
      { name: 'DingTalk', value: 1, color: '#5e35b1' },
      { name: 'WeCom', value: 0, color: '#2196f3' },
      { name: 'WeChat', value: 0, color: '#4caf50' },
      { name: 'Slack', value: 0, color: '#ff9800' }
    ]);
    
    const chartSeries = ref([1, 0, 0, 0]);
    
    // Chart options
    const chartOptions = reactive({
      chart: {
        type: 'donut',
        height: 300,
        fontFamily: `inherit`,
        foreColor: '#a1aab2',
        animations: {
          enabled: true,
          easing: 'easeinout',
          speed: 800,
        },
      },
      colors: ['#5e35b1', '#2196f3', '#4caf50', '#ff9800'],
      labels: ['DingTalk', 'WeCom', 'WeChat', 'Slack'],
      dataLabels: {
        enabled: true,
        formatter: function (val) {
          return val + "%"
        }
      },
      plotOptions: {
        pie: {
          donut: {
            size: '70%',
            labels: {
              show: true,
              name: {
                show: true,
                fontSize: '14px',
                fontWeight: 600,
                color: '#a1aab2',
                offsetY: -10
              },
              value: {
                show: true,
                fontSize: '16px',
                fontWeight: 700,
                color: '#2c3e50',
                offsetY: 16,
                formatter: function (val) {
                  return val
                }
              },
              total: {
                show: true,
                showAlways: false,
                label: 'Total',
                fontSize: '14px',
                fontWeight: 600,
                color: '#a1aab2',
                formatter: function (w) {
                  return w.globals.seriesTotals.reduce((a, b) => {
                    return a + b
                  }, 0)
                }
              }
            }
          }
        }
      },
      legend: {
        show: false
      },
      tooltip: {
        theme: 'light',
        y: {
          formatter: function (val) {
            return val + ' platforms'
          }
        }
      }
    });
    
    // Methods
    const updatePlatformData = () => {
      // Update based on actual running adapters
      const runningAdapters = platformData.value.length;
      const newSeries = platformData.value.map(item => item.value);
      chartSeries.value = newSeries;
    };
    
    // Lifecycle
    onMounted(() => {
      updatePlatformData();
    });
    
    return {
      t,
      platformData,
      chartOptions,
      chartSeries
    };
  }
};
</script>

<style scoped>
.chart-card {
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
}

.chart-container {
  position: relative;
  width: 100%;
}

.platform-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
</style>