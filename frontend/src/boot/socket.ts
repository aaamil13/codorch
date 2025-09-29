import { boot } from 'quasar/wrappers';
import { io, Socket } from 'socket.io-client';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $socket: Socket;
  }
}

// Create socket.io instance
const socket = io(process.env.WS_BASE_URL || 'http://localhost:8000', {
  autoConnect: false,
  transports: ['websocket'],
});

export default boot(({ app }) => {
  app.config.globalProperties.$socket = socket;
});

export { socket };
