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

  bool get isConnected => _channel != null;

  void connect() {
    if (_channel != null) return;

    try {
      // Connect to the brain
      final uri = Uri.parse('ws://127.0.0.1:8000/ws');
      _channel = WebSocketChannel.connect(uri);
      _statusController.add(true);

      _channel!.stream.listen(
        (data) {
          try {
            final json = jsonDecode(data);
            _messageController.add(json);
          } catch (e) {
            print("SyncService decode error: $e");
          }
        },
        onDone: () {
          print("SyncService: Connection closed");
          _channel = null;
          _statusController.add(false);
          // Reconnect logic could go here
        },
        onError: (error) {
          print("SyncService error: $error");
          _channel = null;
          _statusController.add(false);
        },
      );
    } catch (e) {
      print("SyncService connection initialization error: $e");
      _statusController.add(false);
    }
  }

  void sendMessage(String text) {
    if (_channel == null) {
      print("SyncService: Not connected, trying to connect...");
      connect();
    }

    final msg = {"type": "chat", "content": text, "user_id": "sentient_user"};
    try {
      _channel?.sink.add(jsonEncode(msg));
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
