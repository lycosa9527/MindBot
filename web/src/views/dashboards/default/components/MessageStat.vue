<template>
  <v-card elevation="1" class="chart-card">
    <v-card-text>
      <div class="d-flex justify-space-between align-center mb-6">
        <div>
          <h3 class="text-h5 font-weight-bold">{{ t('charts.messageTrend.title') }}</h3>
          <p class="text-body-2 text-medium-emphasis">{{ t('charts.messageTrend.subtitle') }}</p>
        </div>
        
        <div class="d-flex align-center gap-4">
          <v-select
            v-model="selectedTimeRange"
            :items="timeRanges"
            item-title="label"
            item-value="value"
            variant="outlined"
            density="compact"
            hide-details
            style="min-width: 120px;"
            @update:model-value="updateChart"
          />
          <v-btn
            icon="mdi-refresh"
            variant="text"
            size="small"
            :loading="loading"
            @click="updateChart"
          />
        </div>
      </div>

      <div class="d-flex justify-space-between align-center mb-6">
        <div class="d-flex align-center gap-6">
          <div>
            <div class="text-h4 font-weight-bold text-primary">{{ totalMessages }}</div>
            <div class="text-body-2 text-medium-emphasis">{{ t('charts.messageTrend.totalMessages') }}</div>
          </div>
          <div>
            <div class="text-h5 font-weight-bold">{{ dailyAverage }}</div>
            <div class="text-body-2 text-medium-emphasis">{{ t('charts.messageTrend.dailyAverage') }}</div>
          </div>
          <div>
            <div class="d-flex align-center">
              <v-icon 
                :icon="growthRate >= 0 ? 'mdi-trending-up' : 'mdi-trending-down'"
                :color="growthRate >= 0 ? 'success' : 'error'"
                size="small"
                class="mr-1"
              />
              <span 
                class="text-h6 font-weight-bold"
                :class="growthRate >= 0 ? 'text-success' : 'text-error'"
              >
                {{ Math.abs(growthRate) }}%
              </span>
            </div>
            <div class="text-body-2 text-medium-emphasis">{{ t('charts.messageTrend.growthRate') }}</div>
          </div>
        </div>
      </div>

      <div class="chart-container">
        <apexchart 
          type="area" 
          height="280" 
          :options="chartOptions" 
          :series="chartSeries" 
          ref="chart"
        />
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { useModuleI18n } from '@/i18n/composables';

export default {
  name: 'MessageStat',
  props: ['stat'],
  setup() {
    const { tm: t } = useModuleI18n('features/dashboard');
    
    // Reactive data
    const totalMessages = ref('0');
    const dailyAverage = ref('0');
    const growthRate = ref(0);
    const loading = ref(false);
    const selectedTimeRange = ref(null);
    const timeRanges = ref([]);
    const chartSeries = ref([{ name: 'Messages', data: [] }]);
    
    // Chart options
    const chartOptions = reactive({
      chart: {
        type: 'area',
        height: 400,
        fontFamily: `inherit`,
        foreColor: '#a1aab2',
        toolbar: {
          show: true,
          tools: {
            download: true,
            selection: false,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
          },
        },
        animations: {
          enabled: true,
          easing: 'easeinout',
          speed: 800,
        },
      },
      colors: ['#5e35b1'],
      fill: {
        type: 'solid',
        opacity: 0.3,
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      markers: {
        size: 3,
        strokeWidth: 2,
        hover: {
          size: 5,
        }
      },
      tooltip: {
        theme: 'light',
        x: {
          format: 'yyyy-MM-dd HH:mm'
        },
        y: {
          title: {
            formatter: () => ''
          }
        },
      },
      xaxis: {
        type: 'datetime',
        title: {
          text: ''
        },
        labels: {
          formatter: function (value) {
            return new Date(value).toLocaleString('en-US', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            });
          }
        },
        tooltip: {
          enabled: false
        }
      },
      yaxis: {
        title: {
          text: ''
        },
        min: function(min) {
          return min < 10 ? 0 : Math.floor(min * 0.8);
        },
      },
      grid: {
        borderColor: "gray100",
        row: {
          colors: ['transparent', 'transparent'],
          opacity: 0.2
        },
        column: {
          colors: ['transparent', 'transparent'],
        },
        padding: {
          left: 0,
          right: 0
        }
      }
    });
    
    // Methods
    const formatNumber = (num) => {
      return new Intl.NumberFormat('en-US').format(num);
    };
    
    const generateMockData = () => {
      // Generate mock time series data
      const now = new Date();
      const data = [];
      let total = 0;
      
      for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        const messages = Math.floor(Math.random() * 50) + 10;
        data.push([time.getTime(), messages]);
        total += messages;
      }
      
      chartSeries.value[0].data = data;
      totalMessages.value = formatNumber(total);
      dailyAverage.value = formatNumber(Math.round(total / 24));
      growthRate.value = Math.floor(Math.random() * 40) - 20; // Random growth rate
    };
    
    const updateChart = () => {
      generateMockData();
    };
    
    // Lifecycle
    onMounted(() => {
      // Initialize time range options
      timeRanges.value = [
        { label: t('charts.messageTrend.timeRanges.1day'), value: 86400 },
        { label: t('charts.messageTrend.timeRanges.3days'), value: 259200 },
        { label: t('charts.messageTrend.timeRanges.1week'), value: 604800 },
        { label: t('charts.messageTrend.timeRanges.1month'), value: 2592000 },
      ];
      selectedTimeRange.value = timeRanges.value[0];
      
      // Generate mock data for demo
      generateMockData();
    });
    
    return {
      t,
      totalMessages,
      dailyAverage,
      growthRate,
      loading,
      selectedTimeRange,
      timeRanges,
      chartOptions,
      chartSeries,
      updateChart
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
</style>