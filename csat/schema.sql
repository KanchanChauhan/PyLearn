drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  quality_imp  text,
  value_imp  text,
  purchase_imp text,
  usage_imp  text,
  avg_score text,
  feedback text
);