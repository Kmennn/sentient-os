import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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
  Uint8List? _currentImage;
  List<Uint8List> _recentImages = []; // Last 5

  String _ocrText = "";
  List<dynamic> _tags = [];
  String _summary = "";
  String _activeWindow = "Unknown";
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
          final bytes = base64Decode(data['image']);
          setState(() {
            _currentImage = bytes;
            if (_recentImages.length >= 5) _recentImages.removeAt(0);
            _recentImages.add(bytes);
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
          _summary =
              result['summary']['summary'] ??
              (result['summary'] is String ? result['summary'] : "No summary.");
          _tags = result['tags'] ?? [];
          _activeWindow = result['active_window'] ?? "Unknown";
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

  void _copyOcr() {
    Clipboard.setData(ClipboardData(text: _ocrText));
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text("OCR Text Copied!")));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1E1E1E),
      appBar: AppBar(
        title: const Text("Vision Pipeline"),
        backgroundColor: Colors.transparent,
      ),
      body: Column(
        children: [
          // Main Content
          Expanded(
            flex: 3,
            child: Row(
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
                    child: _currentImage != null
                        ? ClipRRect(
                            borderRadius: BorderRadius.circular(12),
                            child: Image.memory(
                              _currentImage!,
                              fit: BoxFit.contain,
                            ),
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
                        Row(
                          children: [
                            ElevatedButton.icon(
                              onPressed: _isLoading ? null : _analyzeScreen,
                              icon: const Icon(Icons.visibility),
                              label: Text(
                                _isLoading ? "Analyzing..." : "See Screen",
                              ),
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 24,
                                  vertical: 16,
                                ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            IconButton(
                              onPressed: _ocrText.isNotEmpty ? _copyOcr : null,
                              icon: const Icon(
                                Icons.copy,
                                color: Colors.cyanAccent,
                              ),
                              tooltip: "Copy OCR",
                            ),
                          ],
                        ),
                        const SizedBox(height: 20),
                        Text(
                          "Status: $_status",
                          style: const TextStyle(color: Colors.amber),
                        ),
                        Text(
                          "Active Window: $_activeWindow",
                          style: const TextStyle(color: Colors.cyanAccent),
                        ),
                        const SizedBox(height: 10),

                        // Tags
                        Wrap(
                          spacing: 8,
                          children: _tags
                              .map(
                                (t) => Chip(
                                  label: Text(t.toString()),
                                  backgroundColor: Colors.cyan.withOpacity(0.2),
                                  labelStyle: const TextStyle(
                                    color: Colors.white,
                                  ),
                                ),
                              )
                              .toList(),
                        ),

                        const Divider(color: Colors.white24),
                        const Text(
                          "Summary:",
                          style: TextStyle(
                            color: Colors.white70,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.all(8),
                          width: double.infinity,
                          color: Colors.black26,
                          child: Text(
                            _summary,
                            style: const TextStyle(color: Colors.white),
                          ),
                        ),

                        const SizedBox(height: 10),
                        const Text(
                          "OCR Text Fragment:",
                          style: TextStyle(
                            color: Colors.white70,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Expanded(
                          child: Container(
                            padding: const EdgeInsets.all(8),
                            width: double.infinity,
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
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Bottom: Thumbnails
          Container(
            height: 100,
            padding: const EdgeInsets.all(8),
            color: Colors.black12,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: _recentImages.length,
              itemBuilder: (context, index) {
                // Show most recent at end? Or reverse?
                // List adds to end, so index is older -> newer?
                final img =
                    _recentImages[_recentImages.length -
                        1 -
                        index]; // Show newest first
                return GestureDetector(
                  onTap: () {
                    setState(() {
                      _currentImage = img;
                    });
                  },
                  child: Container(
                    margin: const EdgeInsets.only(right: 8),
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: _currentImage == img
                            ? Colors.cyan
                            : Colors.white12,
                        width: 2,
                      ),
                    ),
                    child: Image.memory(img),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
