import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';

class VisionPage extends StatefulWidget {
  const VisionPage({super.key});

  @override
  State<VisionPage> createState() => _VisionPageState();
}

class _VisionPageState extends State<VisionPage> {
  bool _isLoading = false;
  Uint8List? _lastImage;
  String _ocrText = "";
  String _summary = "";
  String _status = "Ready to see.";

  Future<void> _analyzeScreen() async {
    setState(() {
      _isLoading = true;
      _status = "Capturing & Analyzing...";
    });

    try {
      // 1. Get Screenshot from Body for Preview
      final imgResp = await http.get(
        Uri.parse("http://localhost:8001/vision/screenshot"),
      );
      if (imgResp.statusCode == 200) {
        final data = json.decode(imgResp.body);
        if (data['image'] != null) {
          setState(() {
            _lastImage = base64Decode(data['image']);
          });
        }
      }

      // 2. Trigger Brain Analysis
      final brainResp = await http.post(
        Uri.parse("http://localhost:8000/v1/vision/analyze"),
      );

      if (brainResp.statusCode == 200) {
        final result = json.decode(brainResp.body);
        setState(() {
          _ocrText = result['ocr_text'] ?? "No text found.";
          _summary = result['summary'] ?? "No summary.";
          _status = "Analysis Complete.";
        });
      } else {
        setState(() {
          _status = "Brain Error: ${brainResp.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _status = "Connection Error: $e";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E1E),
      appBar: AppBar(
        title: const Text("Vision Pipeline"),
        backgroundColor: Colors.transparent,
      ),
      body: Row(
        children: [
          // Left: Image Preview
          Expanded(
            flex: 1,
            child: Container(
              margin: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.white24),
                borderRadius: BorderRadius.circular(12),
              ),
              child: _lastImage != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.memory(_lastImage!, fit: BoxFit.contain),
                    )
                  : const Center(
                      child: Text(
                        "No Image Captured",
                        style: TextStyle(color: Colors.white54),
                      ),
                    ),
            ),
          ),

          // Right: Analysis Controls
          Expanded(
            flex: 1,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ElevatedButton.icon(
                    onPressed: _isLoading ? null : _analyzeScreen,
                    icon: const Icon(Icons.visibility),
                    label: Text(_isLoading ? "Analyzing..." : "See Screen"),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 16,
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  Text(
                    "Status: $_status",
                    style: const TextStyle(color: Colors.amber),
                  ),
                  const Divider(color: Colors.white24),
                  const Text(
                    "OCR Text:",
                    style: TextStyle(
                      color: Colors.white70,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Expanded(
                    child: Container(
                      padding: const EdgeInsets.all(8),
                      color: Colors.black26,
                      child: SingleChildScrollView(
                        child: Text(
                          _ocrText,
                          style: const TextStyle(
                            color: Colors.white60,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    "Summary:",
                    style: TextStyle(
                      color: Colors.white70,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.all(8),
                    color: Colors.black26,
                    child: Text(
                      _summary,
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
