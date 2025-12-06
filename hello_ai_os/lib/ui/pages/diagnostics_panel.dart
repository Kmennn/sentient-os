import 'package:flutter/material.dart';
import 'package:hello_ai_os/services/sync_service.dart';
import 'package:hello_ai_os/ui/widgets/glass_container.dart';

class DiagnosticsPanel extends StatefulWidget {
  final Map<String, dynamic> bodyStats;
  const DiagnosticsPanel({super.key, required this.bodyStats});

  @override
  State<DiagnosticsPanel> createState() => _DiagnosticsPanelState();
}

class _DiagnosticsPanelState extends State<DiagnosticsPanel> {
  List<dynamic> _memoryDump = [];

  @override
  void initState() {
    super.initState();
    syncService.messages.listen((msg) {
      if (mounted && msg['type'] == 'memory.dump.result') {
        setState(() {
          _memoryDump = msg['payload'];
        });
      }
    });
    syncService.requestMemoryDump();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black.withOpacity(0.8),
      appBar: AppBar(
        title: const Text("SYSTEM DIAGNOSTICS"),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Body Stats
            const Text("BODY TELEMETRY", style: TextStyle(color: Colors.cyan)),
            const SizedBox(height: 8),
            GlassContainer(
              padding: const EdgeInsets.all(16),
              child: Text(
                widget.bodyStats.toString().split(',').join('\n'),
                style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
              ),
            ),

            const SizedBox(height: 24),

            // Brain Memory
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  "BRAIN MEMORY (Active Session)",
                  style: TextStyle(color: Colors.purpleAccent),
                ),
                IconButton(
                  icon: const Icon(
                    Icons.refresh,
                    size: 20,
                    color: Colors.purpleAccent,
                  ),
                  onPressed: () => syncService.requestMemoryDump(),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Expanded(
              child: GlassContainer(
                child: ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: _memoryDump.length,
                  itemBuilder: (context, i) {
                    final m = _memoryDump[i];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 8.0),
                      child: Text(
                        "[${m['role'].toUpperCase()}] ${m['content']}",
                        style: const TextStyle(
                          fontSize: 12,
                          color: Colors.white70,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
