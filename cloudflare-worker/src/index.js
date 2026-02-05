/**
 * Cloudflare Cron Worker for Padosi Politics
 * 
 * Architecture:
 * - Frontend: Cloudflare Pages (padosi-politics.pages.dev)
 * - Backend: PythonAnywhere (YOUR_USERNAME.pythonanywhere.com)
 * - Cron: This Cloudflare Worker
 * 
 * Setup:
 * 1. Deploy: cd cloudflare-worker && npx wrangler deploy
 * 2. Set secrets in Cloudflare Dashboard:
 *    - BACKEND_URL: https://YOUR_USERNAME.pythonanywhere.com
 *    - CRON_SECRET: your-cron-secret
 */

export default {
	// HTTP handler for manual testing
	async fetch(request, env, ctx) {
		const url = new URL(request.url);
		
		// Health check
		if (url.pathname === '/') {
			return new Response(JSON.stringify({
				service: 'Padosi Politics Cron Worker',
				status: 'running',
				endpoints: {
					'/run': 'Run all tasks manually',
					'/run/escalate': 'Run escalation only',
					'/run/reminders': 'Run reminders only',
					'/run/cleanup': 'Run cleanup only',
					'/status': 'Check backend status'
				}
			}, null, 2), {
				headers: { 'Content-Type': 'application/json' }
			});
		}
		
		// Check backend health
		if (url.pathname === '/status') {
			try {
				const response = await fetch(`${env.BACKEND_URL}/api/health`, {
					headers: { 'User-Agent': 'Cloudflare-Worker' }
				});
				const data = await response.json();
				return new Response(JSON.stringify({
					backend_url: env.BACKEND_URL,
					backend_status: response.ok ? 'healthy' : 'unhealthy',
					backend_response: data
				}, null, 2), {
					headers: { 'Content-Type': 'application/json' }
				});
			} catch (error) {
				return new Response(JSON.stringify({
					backend_url: env.BACKEND_URL,
					backend_status: 'unreachable',
					error: error.message
				}, null, 2), {
					status: 503,
					headers: { 'Content-Type': 'application/json' }
				});
			}
		}
		
		// Run all tasks
		if (url.pathname === '/run') {
			const results = await runAllTasks(env);
			return new Response(JSON.stringify(results, null, 2), {
				headers: { 'Content-Type': 'application/json' }
			});
		}
		
		// Run specific task
		if (url.pathname.startsWith('/run/')) {
			const taskName = url.pathname.replace('/run/', '');
			const taskMap = {
				'escalate': '/api/cron/escalate',
				'reminders': '/api/cron/reminders',
				'cleanup': '/api/cron/cleanup'
			};
			
			if (taskMap[taskName]) {
				const result = await runTask(env, taskName, taskMap[taskName]);
				return new Response(JSON.stringify(result, null, 2), {
					headers: { 'Content-Type': 'application/json' }
				});
			}
		}
		
		return new Response('Not Found', { status: 404 });
	},

	// Scheduled cron handler
	async scheduled(event, env, ctx) {
		console.log(`Cron triggered: ${event.cron} at ${new Date().toISOString()}`);
		ctx.waitUntil(runAllTasks(env));
	}
};

async function runTask(env, name, endpoint) {
	const startTime = Date.now();
	
	try {
		const response = await fetch(`${env.BACKEND_URL}${endpoint}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'X-Cron-Secret': env.CRON_SECRET,
				'User-Agent': 'Cloudflare-Cron-Worker'
			},
			// PythonAnywhere may be slow to wake up
			cf: { timeout: 30000 }
		});
		
		let data;
		try {
			data = await response.json();
		} catch {
			data = await response.text();
		}
		
		return {
			task: name,
			success: response.ok,
			status: response.status,
			duration_ms: Date.now() - startTime,
			data
		};
	} catch (error) {
		return {
			task: name,
			success: false,
			error: error.message,
			duration_ms: Date.now() - startTime
		};
	}
}

async function runAllTasks(env) {
	const tasks = [
		{ name: 'escalation', endpoint: '/api/cron/escalate' },
		{ name: 'reminders', endpoint: '/api/cron/reminders' },
		{ name: 'cleanup', endpoint: '/api/cron/cleanup' }
	];
	
	const results = [];
	
	// Run tasks sequentially to not overwhelm PythonAnywhere
	for (const task of tasks) {
		console.log(`Running task: ${task.name}`);
		const result = await runTask(env, task.name, task.endpoint);
		results.push(result);
		console.log(`Task ${task.name}: ${result.success ? 'SUCCESS' : 'FAILED'}`);
	}
	
	return {
		timestamp: new Date().toISOString(),
		backend_url: env.BACKEND_URL,
		total_tasks: tasks.length,
		successful: results.filter(r => r.success).length,
		failed: results.filter(r => !r.success).length,
		results
	};
}
