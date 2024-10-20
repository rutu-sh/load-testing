import http from 'k6/http';
import { sleep } from 'k6';

const url = process.env.URL || 'https://test.k6.io';

export const options = {
};

export default function() {
  http.get(url);
}