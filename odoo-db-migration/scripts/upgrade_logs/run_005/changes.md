# Upgrade Changes Log — run_005

## Metadata
- **Run:** run_005
- **Date:** Thu Apr 16 16:42:21 WIB 2026
- **Dump:** /Users/tri-mac/roedl-migration-20260416_151253/roedl_dump_fixed2_20260416_162735.sql
- **Target:** Odoo 19.0
- **Status:** FAILED — errors detected

## Error Summary
```
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/d5/d5cce68bf4bb4ab57beaf766f3fb775cf8df0c83'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
FileNotFoundError: [Errno 2] No such file or directory: '/home/odoo/.local/share/Odoo/filestore/db_4191479/bc/bcb0b0aad1fc08833cb14c6a23dee942a17e1f53'
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//div[hasclass(&#39;settings&#39;)]/div[@data-key=&#39;account&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//button[@name=&#39;action_assign_to_me&#39;]">' cannot be located in parent view
ValueError: Element '<xpath expr="//field[@name=&#39;deposit_taxes_id&#39;]">' cannot be located in parent view
```

## Categories Detected

## Files Generated
- Log: /Users/tri-mac/.claude/skills/odoo-module-migration/scripts/upgrade_logs/run_005/upgrade.log
- SQL Fix: /Users/tri-mac/.claude/skills/odoo-module-migration/scripts/upgrade_logs/run_005/fix_run005.sql

## Next Steps
1. Review /Users/tri-mac/.claude/skills/odoo-module-migration/scripts/upgrade_logs/run_005/fix_run005.sql — edit SQL as needed for your database
2. Apply fixes: psql -h localhost -U odoo -d target_db -f /Users/tri-mac/.claude/skills/odoo-module-migration/scripts/upgrade_logs/run_005/fix_run005.sql
3. Export new dump after applying fixes
4. Re-run: ./odoo_upgrade.sh fixed_dump.sql 19.0
   (Will automatically use run_006)
