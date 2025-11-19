'use client';

import { Radar, RadarChart as RechartsRadar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { RadarChartData } from '@/lib/api';

interface RadarChartProps {
  data: RadarChartData;
}

export default function RadarChart({ data }: RadarChartProps) {
  const chartData = [
    { subject: 'Hook', value: data.hook, fullMark: 100 },
    { subject: 'Originality', value: data.originality, fullMark: 100 },
    { subject: 'Emotion', value: data.emotion, fullMark: 100 },
    { subject: 'Radio Friendly', value: data.radio_friendly, fullMark: 100 },
    { subject: 'Sound Design', value: data.sound_design, fullMark: 100 },
  ];

  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
      <h3 className="text-xl font-semibold text-white mb-4">Performance Breakdown</h3>
      <ResponsiveContainer width="100%" height={400}>
        <RechartsRadar data={chartData}>
          <PolarGrid stroke="#444" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: '#999', fontSize: 12 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: '#666' }}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="#0ea5e9"
            fill="#0ea5e9"
            fillOpacity={0.6}
          />
        </RechartsRadar>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-5 gap-3 text-sm">
        <div>
          <div className="font-medium text-white">Hook: {data.hook.toFixed(0)}</div>
          <div className="text-gray-400 text-xs">Catchiness</div>
        </div>
        <div>
          <div className="font-medium text-white">Originality: {data.originality.toFixed(0)}</div>
          <div className="text-gray-400 text-xs">Uniqueness</div>
        </div>
        <div>
          <div className="font-medium text-white">Emotion: {data.emotion.toFixed(0)}</div>
          <div className="text-gray-400 text-xs">Impact</div>
        </div>
        <div>
          <div className="font-medium text-white">Radio: {data.radio_friendly.toFixed(0)}</div>
          <div className="text-gray-400 text-xs">Commercial</div>
        </div>
        <div>
          <div className="font-medium text-white">Sound: {data.sound_design.toFixed(0)}</div>
          <div className="text-gray-400 text-xs">Production</div>
        </div>
      </div>
    </div>
  );
}
