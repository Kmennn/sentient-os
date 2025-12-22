import 'dart:async';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';
import 'package:flutter/foundation.dart';

class StateStreamService {
  static final StateStreamService _instance = StateStreamService._internal();
  factory StateStreamService() => _instance;

  StateStreamService._internal() {
    _connect();
  }

  final _controller = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get stateStream => _controller.stream;

  // Cache last known state so UI can show something immediately
  Map<String, dynamic> _lastState = {};
  Map<String, dynamic> get lastState => _lastState;

  WebSocketChannel? _channel;

  void _connect() {
    debugPrint("Connecting to Brain State Stream...");
    try {
      _channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8000/ws'));

      _channel!.stream.listen(
        (message) {
          try {
            final data = jsonDecode(message);
            _lastState = data;
            _controller.add(data);
          } catch (e) {
            debugPrint("Error parsing stream data: $e");
          }
        },
        onError: (error) {
          debugPrint("Stream Error: $error");
          // Reconnect logic could go here
        },
        onDone: () => debugPrint("Stream Closed"),
      );
    } catch (e) {
      debugPrint("Connection failed: $e");
    }
  }

  void close() {
    _channel?.sink.close();
    _controller.close();
  }
}

// Global accessor if needed, or use StateStreamService() factory
final stateStreamService = StateStreamService();
