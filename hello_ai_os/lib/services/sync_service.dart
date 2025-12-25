import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter/foundation.dart';

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
      debugPrint("SyncService: Connecting...");
      final uri = Uri.parse('ws://127.0.0.1:8000/ws');
      debugPrint("SyncService: Connecting to $uri");
      _channel = WebSocketChannel.connect(uri);

      debugPrint(
        "SyncService: WebSocket channel created, setting up listeners",
      );
      _reconnectTimer?.cancel();

      _channel!.stream.listen(
        (data) {
          try {
            debugPrint(
              "SyncService: Received data: ${data.toString().substring(0, 100)}...",
            );

            // Set status to connected on first message
            if (_statusController.hasListener) {
              _statusController.add(true);
            }

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
            debugPrint("SyncService decode error: $e");
          }
        },
        onDone: () {
          debugPrint("SyncService: Connection closed");
          _channel = null;
          _statusController.add(false);
          _scheduleReconnect();
        },
        onError: (error) {
          debugPrint("SyncService error: $error");
          _channel = null;
          _statusController.add(false);
          _scheduleReconnect();
        },
      );
      debugPrint("SyncService: Stream listeners attached successfully");
    } catch (e) {
      debugPrint("SyncService connection initialization error: $e");
      _statusController.add(false);
      _scheduleReconnect();
    }
  }

  void _scheduleReconnect() {
    if (_channel != null) return;

    const delay = Duration(seconds: 3);
    debugPrint("SyncService: Reconnecting in 3s...");
    _reconnectTimer = Timer(delay, () {
      connect();
    });
  }

  void sendVoiceStart() {
    // Signal brain we are starting voice
  }

  void sendMessage(String text) {
    if (_channel == null) {
      debugPrint("SyncService: Not connected, trying to connect...");
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
      debugPrint("SyncService send error: $e");
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
