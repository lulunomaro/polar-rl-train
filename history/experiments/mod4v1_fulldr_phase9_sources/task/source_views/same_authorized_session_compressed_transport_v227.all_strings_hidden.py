"""<string-1>"""
from pathlib import Path
from compression import zstd
import importlib, runpy, sys
B = Path(__file__).resolve().parent
W = B.parent.parent
ORIGINAL = Path('<string-2>')

class SameCompressedSession:

    def open(self, *, encoding):
        assert encoding == '<string-3>'
        return zstd.open(str(ORIGINAL) + '<string-4>', '<string-5>', encoding=encoding)

def install():
    sys.path.insert(0, str(W / '<string-6>'))
    module = importlib.import_module('<string-7>')
    assert module.SESSION == ORIGINAL
    assert not ORIGINAL.exists() and Path(str(ORIGINAL) + '<string-8>').is_file()
    previous = module.SESSION
    module.SESSION = SameCompressedSession()
    return (module, previous)

def main():
    target = Path(sys.argv[1]).resolve()
    assert target.is_relative_to(B.parent.resolve())
    assert target.name in {'<string-9>', '<string-10>', '<string-11>', '<string-12>', '<string-13>', '<string-14>', '<string-15>', '<string-16>', '<string-17>', '<string-18>', '<string-19>', '<string-20>', '<string-21>', '<string-22>', '<string-23>', '<string-24>', '<string-25>', '<string-26>', '<string-27>', '<string-28>', '<string-29>', '<string-30>', '<string-31>', '<string-32>', '<string-33>', '<string-34>', '<string-35>', '<string-36>', '<string-37>', '<string-38>', '<string-39>', '<string-40>', '<string-41>', '<string-42>', '<string-43>', '<string-44>', '<string-45>', '<string-46>', '<string-47>', '<string-48>', '<string-49>', '<string-50>', '<string-51>', '<string-52>', '<string-53>', '<string-54>', '<string-55>', '<string-56>', '<string-57>', '<string-58>', '<string-59>', '<string-60>', '<string-61>', '<string-62>', '<string-63>', '<string-64>', '<string-65>', '<string-66>', '<string-67>', '<string-68>', '<string-69>', '<string-70>', '<string-71>', '<string-72>', '<string-73>', '<string-74>', '<string-75>', '<string-76>', '<string-77>', '<string-78>', '<string-79>', '<string-80>', '<string-81>', '<string-82>', '<string-83>', '<string-84>', '<string-85>', '<string-86>', '<string-87>', '<string-88>', '<string-89>', '<string-90>', '<string-91>', '<string-92>', '<string-93>', '<string-94>', '<string-95>', '<string-96>', '<string-97>', '<string-98>', '<string-99>', '<string-100>', '<string-101>', '<string-102>', '<string-103>', '<string-104>', '<string-105>', '<string-106>', '<string-107>', '<string-108>', '<string-109>', '<string-110>', '<string-111>', '<string-112>', '<string-113>', '<string-114>', '<string-115>', '<string-116>', '<string-117>', '<string-118>', '<string-119>', '<string-120>', '<string-121>', '<string-122>', '<string-123>', '<string-124>', '<string-125>', '<string-126>', '<string-127>', '<string-128>', '<string-129>', '<string-130>', '<string-131>', '<string-132>', '<string-133>', '<string-134>', '<string-135>', '<string-136>', '<string-137>', '<string-138>', '<string-139>', '<string-140>', '<string-141>', '<string-142>', '<string-143>', '<string-144>', '<string-145>', '<string-146>', '<string-147>', '<string-148>', '<string-149>', '<string-150>', '<string-151>', '<string-152>', '<string-153>', '<string-154>', '<string-155>', '<string-156>', '<string-157>', '<string-158>', '<string-159>', '<string-160>', '<string-161>', '<string-162>', '<string-163>', '<string-164>', '<string-165>', '<string-166>', '<string-167>', '<string-168>', '<string-169>', '<string-170>', '<string-171>', '<string-172>', '<string-173>', '<string-174>', '<string-175>', '<string-176>', '<string-177>', '<string-178>', '<string-179>', '<string-180>', '<string-181>', '<string-182>', '<string-183>', '<string-184>', '<string-185>', '<string-186>', '<string-187>', '<string-188>', '<string-189>', '<string-190>', '<string-191>', '<string-192>', '<string-193>', '<string-194>', '<string-195>', '<string-196>', '<string-197>', '<string-198>', '<string-199>', '<string-200>', '<string-201>', '<string-202>', '<string-203>', '<string-204>', '<string-205>', '<string-206>', '<string-207>', '<string-208>', '<string-209>', '<string-210>', '<string-211>', '<string-212>', '<string-213>', '<string-214>', '<string-215>', '<string-216>', '<string-217>', '<string-218>', '<string-219>', '<string-220>', '<string-221>', '<string-222>', '<string-223>', '<string-224>', '<string-225>', '<string-226>', '<string-227>', '<string-228>', '<string-229>', '<string-230>', '<string-231>', '<string-232>', '<string-233>', '<string-234>', '<string-235>', '<string-236>', '<string-237>', '<string-238>', '<string-239>', '<string-240>', '<string-241>', '<string-242>', '<string-243>', '<string-244>', '<string-245>', '<string-246>', '<string-247>', '<string-248>', '<string-249>', '<string-250>', '<string-251>', '<string-252>', '<string-253>', '<string-254>', '<string-255>', '<string-256>', '<string-257>', '<string-258>', '<string-259>', '<string-260>', '<string-261>', '<string-262>', '<string-263>', '<string-264>', '<string-265>', '<string-266>', '<string-267>', '<string-268>', '<string-269>', '<string-270>', '<string-271>', '<string-272>', '<string-273>', '<string-274>', '<string-275>', '<string-276>', '<string-277>', '<string-278>', '<string-279>', '<string-280>', '<string-281>', '<string-282>', '<string-283>', '<string-284>', '<string-285>', '<string-286>', '<string-287>', '<string-288>', '<string-289>', '<string-290>', '<string-291>', '<string-292>', '<string-293>', '<string-294>', '<string-295>', '<string-296>', '<string-297>', '<string-298>', '<string-299>', '<string-300>', '<string-301>', '<string-302>', '<string-303>', '<string-304>', '<string-305>', '<string-306>', '<string-307>', '<string-308>', '<string-309>', '<string-310>', '<string-311>', '<string-312>', '<string-313>', '<string-314>'}
    assert target.name != '<string-315>', '<string-316>'
    if target.name == '<string-317>':
        assert len(sys.argv) == 3 and (not sys.argv[2].startswith('<string-318>')) and (sys.argv[2] != '<string-319>'), '<string-320>'
    if target.name == '<string-321>':
        import json, time
        expected = Path(__file__).resolve().parent.parent / '<string-322>'
        assert target.resolve() == (expected / target.name).resolve() and len(sys.argv) == 2
        observed = json.loads((expected / '<string-323>').read_bytes())
        assert observed['<string-324>'] and observed['<string-325>']
        original_go = observed['<string-326>']
        assert set(original_go) == {'<string-327>', '<string-328>', '<string-329>'}
        assert max((x['<string-330>'] for x in original_go.values())) - time.time() <= 900, '<string-331>'
    module, previous = install()
    original_argv = sys.argv
    if target.name == '<string-332>':
        assert len(original_argv) == 3 and original_argv[2] in {'<string-333>', '<string-334>', '<string-335>', '<string-336>'}
        sys.argv = [str(target), original_argv[2]]
    elif target.name == '<string-337>':
        allowed = {'<string-338>', '<string-339>', '<string-340>', '<string-341>'} | {'<string-342>' + str(i).zfill(2) for i in range(1, 21)}
        assert len(original_argv) == 3 and original_argv[2] in allowed
        sys.argv = [str(target), original_argv[2]]
    elif target.name == '<string-343>':
        assert len(original_argv) == 3 and original_argv[2] in {str(i).zfill(2) for i in range(1, 21)}
        sys.argv = [str(target), original_argv[2]]
    elif target.name in {'<string-344>', '<string-345>', '<string-346>'}:
        assert len(original_argv) == 3 and original_argv[2] in {str(i).zfill(2) for i in range(1, 11)}
        sys.argv = [str(target), original_argv[2]]
    else:
        sys.argv = [str(target)]
    try:
        runpy.run_path(str(target), run_name='<string-347>')
    finally:
        module.SESSION = previous
        sys.argv = original_argv
if __name__ == '<string-348>':
    main()