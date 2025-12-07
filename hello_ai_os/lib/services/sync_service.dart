import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class SyncService {
  static final SyncService _instance = SyncService._internal();
  factory SyncService() => _instance;
  SyncService._internal();

  WebSocketChannel? _channel;
  final _messageController = StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get messages => _messageController.stream;

  // v1.2: Status Stream
  final _statusController = StreamController<bool>.broadcast();
  Stream<bool> get connectionStatus => _statusController.stream;

  // v1.3: Wake Event Stream
  final _wakeController = StreamController<bool>.broadcast();
  Stream<bool> get wakeEvents => _wakeController.stream;

  bool get isConnected => _channel != null;
  Timer? _reconnectTimer;

  void connect() {
    if (_channel != null) return;

    try {
      print("SyncService: Connecting...");
      final uri = Uri.parse('ws://127.0.0.1:8000/ws');
      _channel = WebSocketChannel.connect(uri);

      // Wait for connection to be open before resetting retry
      _statusController.add(true);
      _reconnectTimer?.cancel();

      _channel!.stream.listen(
        (data) {
          try {
            final json = jsonDecode(data);

            // v1.3 Handling
            if (json['type'] == 'wake.ack') {
              _wakeController.add(true);
            }
            // Pong handling
            if (json['type'] == 'status.pong' || json['type'] == 'pong') {
              // Reset keepalive timer if we had one
            }

            _messageController.add(json);
          } catch (e) {
            print("SyncService decode error: $e");
          }
        },
        onDone: () {
          print("SyncService: Connection closed");
          _channel = null;
          _statusController.add(false);
          _scheduleReconnect();
        },
        onError: (error) {
          print("SyncService error: $error");
          _channel = null;
          _statusController.add(false);
          _scheduleReconnect();
        },
      );
    } catch (e) {
      print("SyncService connection initialization error: $e");
      _statusController.add(false);
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    if (_channel != null) return;

    const delay = Duration(seconds: 3);
    print("SyncService: Reconnecting in 3s...");
    _reconnectTimer = Timer(delay, () {
      connect();
    });
  }

  void sendVoiceStart() {
    // Signal brain we are starting voice
  }

  void sendMessage(String text) {
    if (_channel == null) {
      print("SyncService: Not connected, trying to connect...");
      connect();
    }

    final msg = {"type": "chat", "content": text, "user_id": "sentient_user"};
    sendMessageJson(msg);
  }

  void sendMessageJson(Map<String, dynamic> data) {
    if (_channel == null) return;
    try {
      _channel?.sink.add(jsonEncode(data));
    } catch (e) {
      print("SyncService send error: $e");
    }
  }

  void sendPing() {
    if (_channel == null) return;
    _channel?.sink.add(jsonEncode({"type": "status.ping"}));
  }

  void requestMemoryDump() {
    if (_channel == null) return;
    _channel?.sink.add(
      jsonEncode({"type": "memory.dump", "user_id": "sentient_user"}),
    );
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
    _statusController.add(false);
  }
}

final syncService = SyncService();
