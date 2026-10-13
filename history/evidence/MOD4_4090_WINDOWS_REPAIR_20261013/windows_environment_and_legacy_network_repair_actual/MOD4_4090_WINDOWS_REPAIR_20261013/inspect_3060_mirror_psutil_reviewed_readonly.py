import inspect_3060_mirror_connection_owner_readonly as original
original.CODE=original.CODE.replace('utf8-sig','utf-8-sig').replace('p.net_connections(kind=', 'p.connections(kind=')
if __name__=='__main__':original.main()
