// Native checks use the patched policy and actual BeginPreload body with a fake record store.
// They do not exercise D3D12, the driver, shader decoding, or the UWP UI.
#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <memory>
#include <numeric>
#include <set>
#include <vector>

using uint32 = std::uint32_t;
using uint64 = std::uint64_t;
#include "Cafe/HW/Latte/Renderer/D3D12/D3D12PreloadPolicy.h"

enum class LogType { Force };
template<typename... Args> void cemuLog_log(LogType, const char*, Args...) {}

struct D3D12PipelineRecordFile
{
	struct Usage { uint32 lastSession; uint32 sessionsUsed; };
	std::vector<uint32> records;
	std::vector<Usage> usage;
	std::set<uint32> startup;
	uint32 session = 22;
	const auto& GetRecords() const { return records; }
	uint32 GetSession() const { return session; }
	Usage GetUsage(uint32 record) const { return usage.at(record); }
	uint32 GetStartupCount() const { return startup.size(); }
	bool IsStartup(uint32 record) const { return startup.count(record) != 0; }
};

struct D3D12PipelineCache
{
	std::unique_ptr<D3D12PipelineRecordFile> m_recordFile;
	struct Preload
	{
		std::vector<uint32> order;
		std::shared_ptr<std::atomic<uint32>> finished;
		std::chrono::steady_clock::time_point start;
		std::size_t limit = 0;
	} m_preload;
	void OpenDiskCaches(uint64) {}
	uint32 BeginPreload(uint64 titleId, bool startupOnly = false, bool includeStale = false);
};

// Extracted unchanged from the applied patch by check_patch.py.
#include "begin_preload.inc"

int main()
{
	constexpr uint64 botw = 0x00050000101c9400ULL;
	// Defaults and other titles retain every combination of the two existing settings.
	const uint64 titles[] = {botw, 0x00050000101c9500ULL, 0x00050000101c9300ULL,
		0x0005000e101c9400ULL, 0x0005000c101c9400ULL, 0ULL};
	for (uint64 title : titles)
		for (bool precompile : {false, true})
			for (bool background : {false, true})
				for (bool optIn : {false, true})
				{
					const auto policy = D3D12PreloadPolicy::Resolve(title, precompile, background, optIn);
					const bool full = title == botw && optIn;
					assert(policy.enabled == (precompile || full));
					assert(policy.startupOnly == (background && !full));
					assert(policy.includeStale == full);
				}

	D3D12PipelineCache cache;
	assert(cache.BeginPreload(botw) == 0); // no record store
	cache.m_recordFile = std::make_unique<D3D12PipelineRecordFile>();
	assert(cache.BeginPreload(botw) == 0); // empty cache
	auto& file = *cache.m_recordFile;
	file.records = {0, 1, 2, 3};
	file.usage = {{22, 2}, {3, 5}, {2, 9}, {1, 5}}; // ages 0, 19, 20, 21
	file.startup = {1, 2};
	assert(cache.BeginPreload(botw) == 2);
	assert((cache.m_preload.order == std::vector<uint32>{1, 0}));
	assert(cache.BeginPreload(botw, true) == 1);
	assert((cache.m_preload.order == std::vector<uint32>{1, 0}));
	// Full preload includes every record, sorted by use (ties preserve original order).
	const auto full = D3D12PreloadPolicy::Resolve(botw, false, true, true);
	assert(full.enabled);
	assert(cache.BeginPreload(botw, full.startupOnly, full.includeStale) == 4);
	assert((cache.m_preload.order == std::vector<uint32>{2, 1, 3, 0}));
	assert(cache.m_preload.limit == cache.m_preload.order.size());
	assert(cache.m_preload.finished->load() == 0);
	// The setting is reversible, including the 20-session boundary.
	assert(cache.BeginPreload(botw) == 2);

	// Existing Quick start fallback: first 400 eligible records, remaining work deferred.
	file.startup.clear();
	file.records.resize(402);
	std::iota(file.records.begin(), file.records.end(), 0);
	file.usage.assign(402, {22, 1});
	assert(cache.BeginPreload(botw, true) == 400);
	assert(cache.m_preload.order.size() == 402);
	assert(cache.m_preload.order.front() == 0 && cache.m_preload.order.back() == 401);
	assert(cache.BeginPreload(botw, false, true) == 402);
	std::cout << "PASS: 48 policy combinations; absent/empty caches; age boundary; full preload; ordering; rollback; Quick start fallback\n";
}
