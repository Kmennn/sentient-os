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

  final _summaryController = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get summaryStream => _summaryController.stream;

  // Cache
  List<Map<String, dynamic>> _lastEvents = [];
  List<Map<String, dynamic>> get lastEvents => _lastEvents;

  Map<String, dynamic> _lastSummary = {};
  Map<String, dynamic> get lastSummary => _lastSummary;

  Timer? _timer;

  void _startPolling() {
    // Initial fetch
    fetchTimeline();
    fetchSummary();
    // Poll
    _timer = Timer.periodic(const Duration(seconds: 30), (_) {
      fetchTimeline();
      fetchSummary();
    });
  }

  Future<void> fetchSummary() async {
    try {
      final uri = Uri.parse("http://127.0.0.1:8000/timeline/summary");
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _lastSummary = data;
        _summaryController.add(data);
      } else {
        print("Summary fetch failed: ${response.statusCode}");
      }
    } catch (e) {
      print("Summary fetch error: $e");
    }
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
    _summaryController.close();
  }
}

final timelineService = TimelineService();
