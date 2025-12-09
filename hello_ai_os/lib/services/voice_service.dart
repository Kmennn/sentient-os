import 'dart:async';
import 'dart:convert';
import 'package:record/record.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class VoiceService {
  final _audioRecorder = AudioRecorder();
  WebSocketChannel? _channel;
  StreamSubscription? _recordSub;

  final _textController = StreamController<String>.broadcast();
  Stream<String> get transcription => _textController.stream;

  bool _isListening = false;
  bool get isListening => _isListening;

  Future<void> start() async {
    if (_isListening) return;

    if (!await _audioRecorder.hasPermission()) {
      _textController.add("[System] Mic permission denied.");
      return;
    }

    try {
      // Connect WS
      _channel = WebSocketChannel.connect(
        Uri.parse('ws://127.0.0.1:8000/v1/voice/stream'),
      );

      // Listen for results
      _channel!.stream.listen(
        (message) {
          try {
            final data = jsonDecode(message);
            if (data['type'] == 'transcription') {
              final text = data['text'];
              // final isFinal = data['is_final'];
              if (text != null && text.isNotEmpty) {
                _textController.add(text);
              }
            }
          } catch (e) {
            // ignore
          }
        },
        onError: (e) {
          _textController.add("[System] Voice WS Error: $e");
        },
      );

      // Start Recording Stream
      // Using WAV. Backend parses header.
      final stream = await _audioRecorder.startStream(
        const RecordConfig(
          encoder: AudioEncoder.wav,
          sampleRate: 16000,
          numChannels: 1,
        ),
      );

      _recordSub = stream.listen((data) {
        _channel?.sink.add(data);
      });

      _isListening = true;
      _textController.add("[System] Listening...");
    } catch (e) {
      _textController.add("[System] Failed to start voice: $e");
      stop();
    }
  }

  Future<void> stop() async {
    _isListening = false;
    await _recordSub?.cancel();
    await _audioRecorder.stop();
    await _channel?.sink.close();
    _channel = null;
    _textController.add("[System] Stopped.");
  }

  void dispose() {
    stop();
    _textController.close();
  }
}

final voiceService = VoiceService();
