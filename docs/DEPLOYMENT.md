# Keelo.ai Deployment Guide

## Overview
This guide covers deploying Keelo.ai to production infrastructure with SSL, monitoring, and CI/CD.

## Infrastructure Options

### Option 1: DigitalOcean (Recommended for Start)
- **Droplet**: $48/month (4GB RAM, 2 vCPUs)
- **Managed Database**: $15/month (1GB RAM, 1 vCPU)
- **Spaces (S3-compatible storage)**: $5/month
- **Total**: ~$68/month

### Option 2: AWS
- **EC2**: t3.medium instance (~$30/month)
- **RDS PostgreSQL**: db.t3.micro (~$15/month)
- **ElastiCache Redis**: cache.t3.micro (~$13/month)
- **S3**: ~$5/month
- **CloudFront CDN**: ~$10/month
- **Total**: ~$73/month

### Option 3: Google Cloud Platform
- **Compute Engine**: e2-medium (~$25/month)
- **Cloud SQL PostgreSQL**: (~$15/month)
- **Memorystore Redis**: (~$15/month)
- **Cloud Storage**: ~$5/month
- **Total**: ~$60/month

## Deployment Steps

### 1. Domain Setup
1. Purchase keelo.ai domain (if not already owned)
2. Configure DNS records:
   ```
   A     @        YOUR_SERVER_IP
   A     www      YOUR_SERVER_IP
   A     api      YOUR_SERVER_IP
   CNAME _domainconnect  _domainconnect.gd.domaincontrol.com
   ```

### 2. Server Setup

#### For DigitalOcean:
```bash
# Create a droplet with Ubuntu 22.04
doctl compute droplet create keelo-prod \
  --image ubuntu-22-04-x64 \
  --size s-2vcpu-4gb \
  --region nyc3 \
  --ssh-keys YOUR_SSH_KEY_ID
```

#### Initial Server Configuration:
```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Run the setup script
curl -O https://raw.githubusercontent.com/yourusername/keelo/main/scripts/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh keelo.ai your-email@example.com
```

### 3. Environment Configuration

Create `.env.production` with your actual values:
```bash
# Generate secure keys
openssl rand -hex 32  # For SECRET_KEY
openssl rand -hex 16  # For DB_PASSWORD

# Edit the .env.production file
nano /opt/keelo/.env.production
```

Required environment variables:
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `DB_PASSWORD`: Strong database password
- `CLAUDE_API_KEY`: Your Anthropic API key
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_PAGESPEED_API_KEY`: Google PageSpeed API key
- `SIMILARWEB_API_KEY`: SimilarWeb API key
- `POSTHOG_API_KEY`: PostHog analytics key

### 4. Deploy Application

#### Manual Deployment:
```bash
# On your local machine
SERVER_IP=YOUR_SERVER_IP ./scripts/deploy.sh
```

#### Using GitHub Actions:
1. Add secrets to your GitHub repository:
   - `SERVER_HOST`: Your server IP
   - `SERVER_USER`: ubuntu (or your SSH user)
   - `SERVER_SSH_KEY`: Your private SSH key

2. Push to main branch to trigger deployment:
```bash
git push origin main
```

### 5. SSL Certificate Setup

The setup script automatically configures Let's Encrypt SSL. To manually renew:
```bash
sudo certbot renew
```

### 6. Database Setup

Initialize the database:
```bash
cd /opt/keelo
docker-compose exec backend alembic upgrade head
```

### 7. Monitoring Setup

#### Application Monitoring
- **PostHog**: Already integrated for user analytics
- **Sentry**: Add `SENTRY_DSN` to track errors

#### Server Monitoring
- **Netdata**: Available at `http://YOUR_SERVER_IP:19999`
- **Docker stats**: `docker stats`
- **Logs**: `docker-compose logs -f`

### 8. Backup Configuration

Automated daily backups are configured. Manual backup:
```bash
/opt/keelo/backup.sh
```

To restore from backup:
```bash
docker-compose exec -T postgres psql -U postgres keelo < backup/keelo_db_TIMESTAMP.sql
```

## Production Checklist

### Security
- [ ] SSL certificates installed and auto-renewing
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] Fail2ban configured for brute force protection
- [ ] Strong passwords for database and Redis
- [ ] Environment variables secured
- [ ] Regular security updates scheduled

### Performance
- [ ] CDN configured (CloudFlare recommended)
- [ ] Redis caching enabled
- [ ] Database indexes optimized
- [ ] Gzip compression enabled
- [ ] Static assets served efficiently

### Monitoring
- [ ] PostHog analytics configured
- [ ] Error tracking (Sentry) configured
- [ ] Server monitoring (Netdata) running
- [ ] Health checks configured
- [ ] Uptime monitoring (UptimeRobot/Pingdom)

### Backup & Recovery
- [ ] Daily automated backups
- [ ] Backup retention policy (7 days local, 30 days S3)
- [ ] Tested restore procedure
- [ ] Disaster recovery plan documented

## Scaling Considerations

### When to Scale
- CPU usage consistently >70%
- Memory usage >80%
- Response times >2 seconds
- >100 concurrent users

### Scaling Options
1. **Vertical Scaling**: Upgrade to larger server
2. **Horizontal Scaling**: Add load balancer + multiple app servers
3. **Database Scaling**: Read replicas, connection pooling
4. **Caching Layer**: Add dedicated Redis cluster

## Maintenance

### Regular Tasks
- **Daily**: Check monitoring dashboards
- **Weekly**: Review error logs, update dependencies
- **Monthly**: Security updates, performance review
- **Quarterly**: Disaster recovery test

### Update Procedure
```bash
# Pull latest code
git pull origin main

# Build and deploy
docker-compose build
docker-compose down
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

## Troubleshooting

### Common Issues

#### 502 Bad Gateway
```bash
# Check if containers are running
docker-compose ps

# Restart services
docker-compose restart

# Check logs
docker-compose logs -f backend
```

#### Database Connection Issues
```bash
# Check database container
docker-compose exec postgres pg_isready

# Reset database connection
docker-compose restart backend celery
```

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL

# Restart services
docker-compose restart
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Review monitoring dashboards
3. Check GitHub Issues
4. Contact support at support@keelo.ai

## Cost Optimization

### Tips to Reduce Costs
1. Use reserved instances (30-50% savings)
2. Implement aggressive caching
3. Use CDN for static assets
4. Optimize database queries
5. Use spot instances for non-critical workers

### Estimated Monthly Costs
- **Minimum (Single Server)**: $50-70/month
- **Recommended (Separate DB)**: $70-100/month
- **Scale (Load Balanced)**: $200-500/month

## Next Steps

After deployment:
1. Configure custom email domain
2. Set up customer support system
3. Implement user authentication
4. Add payment processing
5. Configure analytics dashboards
6. Set up status page (status.keelo.ai)