# Upgrade Changes Log — run_002

## Metadata
- **Run:** run_002
- **Date:** Thu Apr 16 15:52:30 WIB 2026
- **Dump:** /Users/tri-mac/project/porting-0415-3/arkanadigital-roedl-main-6002510_2026-04-15_110617_test_fs.zip
- **Target:** Odoo 19.0
- **Status:** FAILED — errors detected

## Error Summary
```
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191419/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
2026-04-16 03:52:29 ERROR: The upgrade request has failed
```

## Categories Detected

## Files Generated
- Log: /Users/tri-mac/.claude/skills/odoo-module-migration/scripts/upgrade_logs/run_002/upgrade.log
- SQL Fix: /Users/tri-mac/.claude/skills/odoo-module-migration/scripts/upgrade_logs/run_002/fix_run002.sql

## Next Steps
1. Review /Users/tri-mac/.claude/skills/odoo-module-migration/scripts/upgrade_logs/run_002/fix_run002.sql — edit SQL as needed for your database
2. Apply fixes: psql -h localhost -U odoo -d target_db -f /Users/tri-mac/.claude/skills/odoo-module-migration/scripts/upgrade_logs/run_002/fix_run002.sql
3. Export new dump after applying fixes
4. Re-run: ./odoo_upgrade.sh fixed_dump.sql 19.0
   (Will automatically use run_003)
