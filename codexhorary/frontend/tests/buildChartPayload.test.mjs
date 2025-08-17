import assert from 'assert';
import { buildChartPayload } from '../src/utils/buildChartPayload.js';

const chart = {
  id: 1,
  question: 'Will this pass?',
  tags: ['general'],
  chart_data: {
    timezone_info: {
      utc_time: '2024-05-01T20:00:00Z',
      timezone: 'America/New_York'
    },
    houses: {},
    rulers: {},
    aspects: [],
    planets: {}
  },
  traditional_factors: {},
  solar_factors: {},
  reasoning: []
};

const payload = buildChartPayload(chart, false);
assert.equal(payload.asked_at_utc, '2024-05-01T20:00:00.000Z');
const expectedLocal = new Date('2024-05-01T20:00:00Z').toLocaleString('en-US', { timeZone: 'America/New_York' });
assert.equal(payload.asked_at_local, expectedLocal);
console.log('buildChartPayload asked_at times OK');
