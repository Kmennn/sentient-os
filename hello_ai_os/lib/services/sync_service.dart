import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter/foundation.dart';

/// P2.5: Brain connection states
enum BrainState {
  disconnected, // RED - not connected
  connected, // YELLOW - connected but not ready
  ready, // GREEN - brain.ready received
}

class SyncService {
  static final SyncService _instance = SyncService._internal();
  factory SyncService() => _instance;
  SyncService._internal();

  WebSocketChannel? _channel;
  final _messageController = StreamController<Map<String, dynamic>>.broadcast();

  Stream<Map<String, dynamic>> get messages => _messageController.stream;

  // P2.5: Brain state stream (replaces simple bool)
  final _brainStateController = StreamController<BrainState>.broadcast();
  Stream<BrainState> get brainStateStream => _brainStateController.stream;
  BrainState _currentBrainState = BrainState.disconnected;
  BrainState get currentBrainState => _currentBrainState;

  // Legacy compatibility - true only when READY (GREEN)
  final _statusController = StreamController<bool>.broadcast();
  Stream<bool> get connectionStatus => _statusController.stream;

  // v1.3: Wake Event Stream
  final _wakeController = StreamController<bool>.broadcast();
  Stream<bool> get wakeEvents => _wakeController.stream;

  bool get isConnected => _channel != null;
  Timer? _reconnectTimer;

  void _updateBrainState(BrainState newState, String reason) {
    _currentBrainState = newState;
    debugPrint("[STATE] BrainState=$newState (reason: $reason)");
    _brainStateController.add(newState);

    // Legacy status: true only when READY
    _statusController.add(newState == BrainState.ready);
  }

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

            final json = jsonDecode(data);
            final msgType = json['type']?.toString() ?? '';
            debugPrint("SyncService: msg type='$msgType'");

            // First message = YELLOW (connected but not ready)
            // BUT: skip this if it's already a brain.ready message
            if (_currentBrainState == BrainState.disconnected &&
                msgType != 'brain.ready') {
              _updateBrainState(BrainState.connected, "first message received");
            }

            // P2.5: Handle brain.ready event - only this makes dot GREEN
            if (msgType == 'brain.ready') {
              final isReady = json['payload']?['ready'] ?? false;
              debugPrint("SyncService: brain.ready event, ready=$isReady");
              if (isReady) {
                _updateBrainState(BrainState.ready, "brain.ready received");
              }
            }

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
          _updateBrainState(BrainState.disconnected, "connection closed");
          _scheduleReconnect();
        },
        onError: (error) {
          debugPrint("SyncService error: $error");
          _channel = null;
          _updateBrainState(BrainState.disconnected, "connection error");
          _scheduleReconnect();
        },
      );
      debugPrint("SyncService: Stream listeners attached successfully");
    } catch (e) {
      debugPrint("SyncService connection initialization error: $e");
      _updateBrainState(BrainState.disconnected, "connection init error");
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

    // P3.1: Generate unique message_id for lifecycle tracking
    final messageId = DateTime.now().millisecondsSinceEpoch.toString();
    final msg = {
      "type": "chat",
      "content": text,
      "user_id": "sentient_user",
      "message_id": messageId, // P3.1: Enable request/response matching
    };
    debugPrint("[P3.1] Sending message_id=$messageId");
    sendMessageJson(msg);
  }

  // P3.1: Send with explicit message_id (returns the ID for tracking)
  String sendMessageWithId(String text) {
    if (_channel == null) {
      debugPrint("SyncService: Not connected, trying to connect...");
      connect();
    }

    final messageId = DateTime.now().millisecondsSinceEpoch.toString();
    final msg = {
      "type": "chat",
      "content": text,
      "user_id": "sentient_user",
      "message_id": messageId,
    };
    debugPrint("[P3.1] Sending message_id=$messageId");
    sendMessageJson(msg);
    return messageId;
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
    _updateBrainState(BrainState.disconnected, "manual disconnect");
  }
}

final syncService = SyncService();
