/**
 * Base class for every participant that communicates only through the
 * ResultMediator (Department Office, Controller, DSW, Student).
 */
public abstract class Colleague {

    protected final ResultMediator mediator;

    protected Colleague(ResultMediator mediator) {
        this.mediator = mediator;
    }
}
