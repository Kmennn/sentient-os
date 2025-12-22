import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

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

  final _confidenceController =
      StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get confidenceStream =>
      _confidenceController.stream;

  // Cache
  List<Map<String, dynamic>> _lastEvents = [];
  List<Map<String, dynamic>> get lastEvents => _lastEvents;

  Map<String, dynamic> _lastSummary = {};
  Map<String, dynamic> get lastSummary => _lastSummary;

  Map<String, dynamic> _lastConfidence = {};
  Map<String, dynamic> get lastConfidence => _lastConfidence;

  Timer? _timer;

  void _startPolling() {
    // Initial fetch
    fetchTimeline();
    fetchSummary();
    fetchConfidence();
    // Poll
    _timer = Timer.periodic(const Duration(seconds: 30), (_) {
      fetchTimeline();
      fetchSummary();
      fetchConfidence();
    });
  }

  Future<void> fetchConfidence() async {
    try {
      final uri = Uri.parse("http://127.0.0.1:8000/system/confidence");
      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _lastConfidence = data;
        _confidenceController.add(data);
      }
    } catch (e) {
      debugPrint("Confidence fetch error: $e");
    }
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
        debugPrint("Summary fetch failed: ${response.statusCode}");
      }
    } catch (e) {
      debugPrint("Summary fetch error: $e");
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
        debugPrint("Timeline fetch failed: ${response.statusCode}");
      }
    } catch (e) {
      debugPrint("Timeline error: $e");
    }
  }

  void dispose() {
    _timer?.cancel();
    _controller.close();
    _summaryController.close();
    _confidenceController.close();
  }
}

final timelineService = TimelineService();
