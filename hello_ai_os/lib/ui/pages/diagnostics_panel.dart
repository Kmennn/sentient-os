import 'package:flutter/material.dart';
import 'package:hello_ai_os/services/sync_service.dart';
import 'package:hello_ai_os/ui/widgets/glass_container.dart';

class DiagnosticsPanel extends StatefulWidget {
  final Map<String, dynamic> bodyStats;
  const DiagnosticsPanel({super.key, required this.bodyStats});

  @override
  State<DiagnosticsPanel> createState() => _DiagnosticsPanelState();
}

class _DiagnosticsPanelState extends State<DiagnosticsPanel>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  List<dynamic> _memoryDump = [];
  final List<String> _eventLog = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);

    // Messaage Listener
    syncService.messages.listen((msg) {
      if (!mounted) return;
      if (msg['type'] == 'memory.dump.result') {
        setState(() {
          _memoryDump = msg['payload'];
        });
      }
      // Listen for action events for the log
      if (msg['type'].toString().startsWith('action.')) {
        setState(() {
          _eventLog.insert(0, "[ACTION] ${msg['type']}: ${msg['payload']}");
        });
      }
    });

    syncService.wakeEvents.listen((_) {
      if (mounted) {
        setState(() {
          _eventLog.insert(
            0,
            "[${DateTime.now().toIso8601String()}] Wake Event",
          );
        });
      }
    });

    syncService.requestMemoryDump();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black.withOpacity(0.9),
      appBar: AppBar(
        title: const Text("DIAGNOSTICS v1.5"),
        backgroundColor: Colors.transparent,
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: "MEMORY"),
            Tab(text: "LIVE LOG"),
            Tab(text: "ACTIONS"),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [_buildMemoryTab(), _buildEventsTab(), _buildActionsTab()],
      ),
    );
  }

  Widget _buildMemoryTab() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                "Active Context",
                style: TextStyle(color: Colors.purpleAccent),
              ),
              IconButton(
                onPressed: () => syncService.requestMemoryDump(),
                icon: const Icon(Icons.refresh),
              ),
            ],
          ),
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
    );
  }

  Widget _buildEventsTab() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          const Text(
            "Live System Events",
            style: TextStyle(color: Colors.greenAccent),
          ),
          const SizedBox(height: 10),
          GlassContainer(
            padding: const EdgeInsets.all(16),
            child: Text(
              widget.bodyStats.toString(),
              style: const TextStyle(fontFamily: 'monospace', fontSize: 10),
            ),
          ),
          const SizedBox(height: 10),
          Expanded(
            child: GlassContainer(
              child: ListView.builder(
                itemCount: _eventLog.length,
                itemBuilder: (context, i) => Padding(
                  padding: const EdgeInsets.all(4.0),
                  child: Text(
                    _eventLog[i],
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 11,
                      color: Colors.green,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionsTab() {
    // Filter logs for actions
    final actions = _eventLog.where((e) => e.contains("[ACTION]")).toList();
    return Padding(
      padding: const EdgeInsets.all(16),
      child: GlassContainer(
        child: ListView.builder(
          itemCount: actions.length,
          itemBuilder: (context, i) {
            return ListTile(
              leading: const Icon(Icons.gavel, color: Colors.amber, size: 14),
              title: Text(
                actions[i].replaceAll("[ACTION] ", ""),
                style: const TextStyle(fontSize: 12, color: Colors.white),
              ),
            );
          },
        ),
      ),
    );
  }
}
