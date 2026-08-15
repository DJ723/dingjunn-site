# 部署到 dingjunn.com

域名目前在阿里云（万网，DNS：`dns15/16.hichina.com`），还没有网站解析。

## 推荐：Vercel（免费静态托管）

### 1. 部署网站文件

任选一种：

**A. 网页拖拽（最简单）**
1. 打开 https://vercel.com/new
2. 注册/登录（可用 GitHub 或邮箱）
3. 把整个 `dingjunn-site` 文件夹拖进去部署
4. 记下生成的临时域名，例如 `xxx.vercel.app`

**B. 命令行（登录后由我执行）**
```bash
cd ~/dingjunn-site
./node_modules/.bin/vercel login
./node_modules/.bin/vercel --prod
./node_modules/.bin/vercel domains add dingjunn.com
```

### 2. 在 Vercel 绑定域名

Project → Settings → Domains → 添加：
- `dingjunn.com`
- `www.dingjunn.com`

### 3. 在阿里云配置 DNS

登录阿里云 → 域名 → `dingjunn.com` → 解析设置，添加：

| 主机记录 | 记录类型 | 记录值 |
|---|---|---|
| `@` | A | `76.76.21.21` |
| `www` | CNAME | `cname.vercel-dns.com` |

（若 Vercel 域名页显示了不同的值，以 Vercel 页面为准。）

等待 5–30 分钟生效，然后访问 https://dingjunn.com

## 备选：Cloudflare Pages

把域名 NS 改到 Cloudflare 后，Pages 可一键托管并自动 HTTPS。适合以后长期维护。
