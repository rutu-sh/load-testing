import http from 'k6/http';
import { sleep } from 'k6';

const url = __ENV.URL || 'https://test.k6.io';

export const options = {
  scenarios: {
    open_model: {
      executor: 'constant-arrival-rate',
    }
  }
};

export default function() {
  http.get(url);
}