import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class TimelineService {
  static final TimelineService _instance = TimelineService._internal();
  factory TimelineService() => _instance;

  TimelineService._internal() {
    _startPolling();
  }

  // Stream controller
  final _controller = StreamController<List<Map<String, dynamic>>>.broadcast();
  Stream<List<Map<String, dynamic>>> get timelineStream => _controller.stream;

  // Cache
  List<Map<String, dynamic>> _lastEvents = [];
  List<Map<String, dynamic>> get lastEvents => _lastEvents;

  Timer? _timer;

  void _startPolling() {
    // Initial fetch
    fetchTimeline();
    // Poll
    _timer = Timer.periodic(
      const Duration(seconds: 30),
      (_) => fetchTimeline(),
    );
  }

  Future<void> fetchTimeline() async {
    try {
      final uri = Uri.parse(
        "http://127.0.0.1:8000/timeline?since_seconds=86400",
      ); // 24h
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        _lastEvents = List<Map<String, dynamic>>.from(data);
        _controller.add(_lastEvents);
      } else {
        print("Timeline fetch failed: ${response.statusCode}");
      }
    } catch (e) {
      print("Timeline error: $e");
    }
  }

  void dispose() {
    _timer?.cancel();
    _controller.close();
  }
}

final timelineService = TimelineService();
