import { Activity, Thermometer, Waves, Radiation, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import type { SensorData } from '@/types';

interface SensorDataPanelProps {
  sensors: SensorData[];
}

export function SensorDataPanel({ sensors }: SensorDataPanelProps) {
  const getSensorIcon = (type: SensorData['type']) => {
    switch (type) {
      case 'seismic': return Activity;
      case 'temperature': return Thermometer;
      case 'flood': return Waves;
      case 'radiation': return Radiation;
      default: return Activity;
    }
  };

  const getSensorColor = (type: SensorData['type']) => {
    switch (type) {
      case 'seismic': return 'text-red-500';
      case 'temperature': return 'text-orange-500';
      case 'flood': return 'text-blue-500';
      case 'radiation': return 'text-yellow-500';
      default: return 'text-gray-500';
    }
  };

  const getSensorBg = (type: SensorData['type']) => {
    switch (type) {
      case 'seismic': return 'bg-red-500/20';
      case 'temperature': return 'bg-orange-500/20';
      case 'flood': return 'bg-blue-500/20';
      case 'radiation': return 'bg-yellow-500/20';
      default: return 'bg-gray-500/20';
    }
  };

  // Mock historical data for charts
  const generateChartData = (baseValue: number) => {
    return Array.from({ length: 20 }, (_, i) => ({
      time: i,
      value: baseValue + (Math.random() - 0.5) * baseValue * 0.2,
    }));
  };

  return (
    <Card className="border-border">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Activity className="w-4 h-4 text-primary" />
          Live Sensor Data
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {sensors.map(sensor => {
          const Icon = getSensorIcon(sensor.type);
          const chartData = generateChartData(sensor.value);
          
          return (
            <div key={sensor.id} className="p-3 bg-muted rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg ${getSensorBg(sensor.type)}`}>
                    <Icon className={`w-4 h-4 ${getSensorColor(sensor.type)}`} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-foreground capitalize">
                      {sensor.type} Sensor
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Lat: {sensor.location[0].toFixed(3)}, Lon: {sensor.location[1].toFixed(3)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-lg font-bold ${getSensorColor(sensor.type)}`}>
                    {sensor.value.toFixed(2)}
                  </p>
                  <p className="text-xs text-muted-foreground">{sensor.unit}</p>
                </div>
              </div>
              
              {/* Mini Chart */}
              <div className="h-16 mt-2">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke={sensor.type === 'seismic' ? '#ef4444' :
                              sensor.type === 'temperature' ? '#f97316' :
                              sensor.type === 'flood' ? '#3b82f6' :
                              '#eab308'}
                      strokeWidth={2}
                      dot={false}
                    />
                    <XAxis hide dataKey="time" />
                    <YAxis hide domain={['auto', 'auto']} />
                    <Tooltip 
                      contentStyle={{ 
                        background: '#1f2937', 
                        border: 'none', 
                        borderRadius: '4px',
                        fontSize: '12px'
                      }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              
              {sensor.anomaly && (
                <div className="flex items-center gap-2 mt-2 p-2 bg-red-500/10 rounded">
                  <AlertTriangle className="w-4 h-4 text-red-500" />
                  <span className="text-xs text-red-500">Anomaly detected - Value exceeds threshold</span>
                </div>
              )}
            </div>
          );
        })}
        
        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-3 pt-2 border-t border-border">
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Active Sensors</p>
            <p className="text-lg font-bold text-foreground">{sensors.length}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-muted-foreground">Anomalies</p>
            <p className="text-lg font-bold text-red-500">
              {sensors.filter(s => s.anomaly).length}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
